FROM rust:slim AS builder
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        pkg-config libfontconfig1-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN apt-get update && apt-get install -y libfontconfig1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN cargo build --release

# The "slim" tag was removed from Docker Hub. Use the official
# "stable-slim" variant instead (verified via the Docker Hub API).
FROM debian:stable-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libfontconfig1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /usr/src/app/target/release/analysis_service ./analysis_service
EXPOSE 8001
CMD ["./analysis_service"]
