from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input format
class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: float


# Telemetry data
data = [
    {"region": "apac", "latency_ms": 159.72, "uptime_pct": 98.558},
    {"region": "apac", "latency_ms": 119.45, "uptime_pct": 98.719},
    {"region": "apac", "latency_ms": 238.18, "uptime_pct": 98.155},
    {"region": "apac", "latency_ms": 174.03, "uptime_pct": 98.054},
    {"region": "apac", "latency_ms": 203.28, "uptime_pct": 98.701},
    {"region": "apac", "latency_ms": 178.28, "uptime_pct": 98.855},
    {"region": "apac", "latency_ms": 182.89, "uptime_pct": 98.199},
    {"region": "apac", "latency_ms": 158.92, "uptime_pct": 97.104},
    {"region": "apac", "latency_ms": 135.35, "uptime_pct": 97.907},
    {"region": "apac", "latency_ms": 143.38, "uptime_pct": 97.763},
    {"region": "apac", "latency_ms": 201.8, "uptime_pct": 97.533},
    {"region": "apac", "latency_ms": 135.11, "uptime_pct": 99.013},

    {"region": "emea", "latency_ms": 145.25, "uptime_pct": 97.186},
    {"region": "emea", "latency_ms": 213.21, "uptime_pct": 98.892},
    {"region": "emea", "latency_ms": 204.28, "uptime_pct": 98.63},
    {"region": "emea", "latency_ms": 198.58, "uptime_pct": 99.32},
    {"region": "emea", "latency_ms": 220.89, "uptime_pct": 98.691},
    {"region": "emea", "latency_ms": 157.04, "uptime_pct": 97.639},
    {"region": "emea", "latency_ms": 130.18, "uptime_pct": 99.276},
    {"region": "emea", "latency_ms": 182.22, "uptime_pct": 98.308},
    {"region": "emea", "latency_ms": 128.67, "uptime_pct": 98.342},
    {"region": "emea", "latency_ms": 212.78, "uptime_pct": 97.115},
    {"region": "emea", "latency_ms": 148.74, "uptime_pct": 99.345},
    {"region": "emea", "latency_ms": 146.42, "uptime_pct": 98.86},

    {"region": "amer", "latency_ms": 133.08, "uptime_pct": 97.831},
    {"region": "amer", "latency_ms": 124.64, "uptime_pct": 97.502},
    {"region": "amer", "latency_ms": 177.27, "uptime_pct": 97.859},
    {"region": "amer", "latency_ms": 179.07, "uptime_pct": 98.204},
    {"region": "amer", "latency_ms": 203.14, "uptime_pct": 98.43},
    {"region": "amer", "latency_ms": 214.08, "uptime_pct": 98.037},
    {"region": "amer", "latency_ms": 181.52, "uptime_pct": 97.346},
    {"region": "amer", "latency_ms": 133.21, "uptime_pct": 99.021},
    {"region": "amer", "latency_ms": 158.35, "uptime_pct": 98.526},
    {"region": "amer", "latency_ms": 231.35, "uptime_pct": 99.324},
    {"region": "amer", "latency_ms": 195.29, "uptime_pct": 97.162},
    {"region": "amer", "latency_ms": 184.02, "uptime_pct": 97.885},
]


def percentile_95(values):
    values = sorted(values)

    position = 0.95 * (len(values) - 1)
    lower = int(position)
    upper = lower + 1

    if upper >= len(values):
        return values[lower]

    fraction = position - lower

    return values[lower] + fraction * (values[upper] - values[lower])


@app.post("/")
def calculate_metrics(request: RequestData):

    response = {}

    for region in request.regions:

        records = [
            row for row in data
            if row["region"] == region
        ]

        if not records:
            continue

        latencies = [
            row["latency_ms"]
            for row in records
        ]

        uptimes = [
            row["uptime_pct"]
            for row in records
        ]

        avg_latency = sum(latencies) / len(latencies)

        p95_latency = percentile_95(latencies)

        avg_uptime = sum(uptimes) / len(uptimes)

        breaches = sum(
            1 for latency in latencies
            if latency > request.threshold_ms
        )

        response[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return response