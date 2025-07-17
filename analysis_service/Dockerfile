FROM rust:1.77 as builder
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        pkg-config libfontconfig1-dev build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/src/app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bullseye-slim
WORKDIR /app
COPY --from=builder /usr/src/app/target/release/analysis_service ./analysis_service
EXPOSE 8001
CMD ["./analysis_service"]
