import json
import time


#from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.functions import MapFunction, KeyedProcessFunction
from pyflink.common.typeinfo import Types


from pyflink.datastream.state import ValueStateDescriptor
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.datastream.connectors.kafka import FlinkKafkaProducer



# =====================================================
# 1️⃣ Flink 执行环境（Windows 本地必须这样）
# =====================================================
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)   # ⚠️ 本地调试必须 1


# =====================================================
# 2️⃣ Kafka Consumer（events topic）
# =====================================================
consumer = FlinkKafkaConsumer(
    topics="events",
    deserialization_schema=SimpleStringSchema(),
    properties={
        "bootstrap.servers": "localhost:9092",
        "group.id": "feature-builder"
    }
)

raw_stream = env.add_source(consumer)


# =====================================================
# 3️⃣ JSON 解析（不用 lambda，避免 PyFlink 炸）
# =====================================================
class ParseJson(MapFunction):
    def map(self, value):
        """
        Kafka 中拿到的是字符串 JSON
        """
        return json.loads(value)


event_stream = (
    raw_stream
    .map(
        ParseJson(),
        output_type=Types.MAP(
            Types.STRING(),
            Types.STRING()   # Kafka 里字段一律 string
        )
    )
    .key_by(lambda x: x["user_id"])  # user_id 这里还是字符串
)


# =====================================================
# 4️⃣ ⭐ 核心：历史特征 + 新数据（State）
# =====================================================
class FeatureProcess(KeyedProcessFunction):

    def open(self, runtime_context):
        descriptor = ValueStateDescriptor(
            "feature_state",
            Types.MAP(Types.STRING(), Types.INT())
        )
        self.feature_state = runtime_context.get_state(descriptor)

    def process_element(self, value, ctx):
        """
        value 示例：
        {
            "user_id": "1",
            "event_type": "click"
        }
        """
        features = self.feature_state.value()

        if features is None:
            features = {
                "click_cnt": 0,
                "purchase_cnt": 0
            }

        event_type = value.get("event_type")

        if event_type == "click":
            features["click_cnt"] += 1
        elif event_type == "purchase":
            features["purchase_cnt"] += 1

        # 更新历史特征
        self.feature_state.update(features)

        result = {
            "user_id": int(value["user_id"]),
            "click_cnt": features["click_cnt"],
            "purchase_cnt": features["purchase_cnt"],
            "updated_at": int(time.time())
        }

        yield json.dumps(result)


# =====================================================
# 5️⃣ Kafka Producer（features topic）
# =====================================================
producer = FlinkKafkaProducer(
    topic="features",
    serialization_schema=SimpleStringSchema(),
    producer_config={
        "bootstrap.servers": "localhost:9092"
    }
)


# =====================================================
# 6️⃣ 组装执行流
# =====================================================
(
    event_stream
    .process(
        FeatureProcess(),
        output_type=Types.STRING()
    )
    .add_sink(producer)
)

env.execute("feature-builder-job")