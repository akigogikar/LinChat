FROM rust:1.77 as builder
WORKDIR /usr/src/app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bullseye-slim
WORKDIR /app
COPY --from=builder /usr/src/app/target/release/analysis_service ./analysis_service
EXPOSE 8001
CMD ["./analysis_service"]
