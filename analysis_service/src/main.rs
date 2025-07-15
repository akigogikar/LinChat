use axum::{routing::post, Router, extract::Multipart, response::Response};
use axum::http::StatusCode;
use polars::prelude::*;
use base64::Engine;
use plotters::prelude::*;
use serde::Serialize;
use calamine::{Reader, open_workbook_auto_from_rs, Data};
use std::net::SocketAddr;
use tracing::{info, error};


#[derive(Serialize)]
struct Stats {
    column: String,
    mean: f64,
    median: f64,
    sum: f64,
}

async fn analyze(mut multipart: Multipart) -> Result<Response, StatusCode> {
    // Expect a single file field named "file"
    let mut data: Option<Vec<u8>> = None;
    while let Some(field) = multipart.next_field().await.unwrap() {
        if let Some(name) = field.name() {
            if name == "file" {
                data = Some(field.bytes().await.unwrap().to_vec());
                break;
            }
        }
    }
    info!("received analysis request");

    let data = data.ok_or(StatusCode::BAD_REQUEST)?;
    // Read Excel data using calamine and convert to Polars DataFrame
    let cursor = std::io::Cursor::new(data);
    let mut workbook = open_workbook_auto_from_rs(cursor).map_err(|_| StatusCode::BAD_REQUEST)?;
    let sheet_name = workbook.sheet_names().get(0).cloned().ok_or(StatusCode::BAD_REQUEST)?;
    let range = workbook.worksheet_range(&sheet_name).map_err(|_| StatusCode::BAD_REQUEST)?;

    let rows: Vec<Vec<Data>> = range.rows().map(|r| r.to_vec()).collect();
    if rows.is_empty() { return Err(StatusCode::BAD_REQUEST); }
    let headers: Vec<String> = rows[0].iter().map(|c| c.to_string()).collect();
    let mut columns: Vec<Vec<Option<f64>>> = vec![Vec::new(); headers.len()];
    for row in rows.iter().skip(1) {
        for (i, cell) in row.iter().enumerate() {
            let val = match cell {
                Data::Float(f) => Some(*f),
                Data::Int(i) => Some(*i as f64),
                Data::String(s) => s.parse::<f64>().ok(),
                _ => None,
            };
            columns[i].push(val);
        }
    }

    let series: Vec<Series> = headers
        .iter()
        .enumerate()
        .map(|(i, name)| Series::new(name.as_str().into(), columns[i].clone()))
        .collect();
    let columns_polars: Vec<Column> = series.into_iter().map(Column::from).collect();
    let df = DataFrame::new(columns_polars).map_err(|_| StatusCode::BAD_REQUEST)?;

    // Compute basic stats for numeric columns
    let mut stats = Vec::new();
    for col in df.get_columns() {
        if let Ok(series) = col.cast(&DataType::Float64) {
            let s = series.f64().unwrap();
            let mean = s.mean().unwrap_or(0.0);
            let median = s.median().unwrap_or(0.0);
            let sum = s.sum().unwrap_or(0.0);
            stats.push(Stats { column: col.name().to_string(), mean, median, sum });
        }
    }

    // Generate chart for first numeric column
    let chart_bytes = if let Some(first) = df.get_columns().iter().find(|c| matches!(c.dtype(), DataType::Float64 | DataType::Int64 | DataType::Int32)) {
        let series = if first.dtype() != &DataType::Float64 { first.cast(&DataType::Float64).unwrap() } else { first.clone() };
        let s = series.f64().unwrap();
        let mut buf = Vec::<u8>::new();
        {
            let root = BitMapBackend::with_buffer(&mut buf, (640, 480)).into_drawing_area();
            root.fill(&WHITE).unwrap();
            let max = s.max().unwrap_or(0.0);
            let min = s.min().unwrap_or(0.0);
            let mut chart = ChartBuilder::on(&root)
                .margin(10)
                .caption(first.name(), ("sans-serif", 20))
                .x_label_area_size(30)
                .y_label_area_size(40)
                .build_cartesian_2d(0usize..s.len(), min..max)
                .unwrap();
            chart.configure_mesh().draw().unwrap();
            chart.draw_series(LineSeries::new(
                s.into_iter().enumerate().map(|(idx, val)| (idx, val.unwrap_or(0.0))),
                &RED,
            )).unwrap();
            root.present().unwrap();
        }
        Some(buf)
    } else {
        None
    };

    let result_json = serde_json::to_string(&stats).unwrap();

    if let Some(img) = chart_bytes {
        let res = Response::builder()
            .status(StatusCode::OK)
            .header("Content-Type", "application/json")
            .header("Chart", base64::engine::general_purpose::STANDARD.encode(&img))
            .body(result_json.into())
            .unwrap();
        Ok(res)
    } else {
        Ok(Response::builder()
            .status(StatusCode::OK)
            .header("Content-Type", "application/json")
            .body(result_json.into())
            .unwrap())
    }
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    let app = Router::new().route("/analysis", post(analyze));
    let addr = SocketAddr::from(([0, 0, 0, 0], 8001));
    info!("Listening on {addr}");
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    if let Err(e) = axum::serve(listener, app).await {
        error!(?e, "server error");
    }
}

