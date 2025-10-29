from pathlib import Path
import sys
import pkgutil
import importlib.util

# Compatibility shim: in Python 3.14+ pkgutil.find_loader was removed.
# Some third-party packages (older versions of Dash) still call
# pkgutil.find_loader(). Provide a small compatibility wrapper that
# returns an importlib spec (truthy when the module can be found).
if not hasattr(pkgutil, "find_loader"):
	from types import SimpleNamespace

	def _find_loader(name):
		"""Approximate the old pkgutil.find_loader behavior using ModuleSpec.

		Return a small loader-like object with a `path` attribute when the
		target is a package (so downstream code that inspects `package.path`
		continues to work), otherwise return an object with `filename` set.
		"""
		try:
			spec = importlib.util.find_spec(name)
		except Exception:
			return None
		if spec is None:
			return None

		# If spec.submodule_search_locations is set, it's a package. Use the
		# first location as a loader-like `path` attribute.
		submods = getattr(spec, "submodule_search_locations", None)
		if submods:
			path = submods[0]
			return SimpleNamespace(path=path, _path=list(submods), filename=spec.origin)

		# Otherwise fall back to using origin as filename
		return SimpleNamespace(filename=getattr(spec, "origin", None))

	setattr(pkgutil, "find_loader", _find_loader)

import pandas as pd
from dash import Dash, html, dcc, Input, Output, no_update
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


EXCEL_FILENAME = "시간별 일별동향_20251030_000958.xls"

# Define consistent colors for each series
SERIES_COLORS = {
    "지수": "#1f77b4",     # blue for index
    "외국인": "#2ecc71",   # green for foreign
    "개인": "#e74c3c",     # red for individual
    "기관종합": "#3498db"  # light blue for institutional
}


def load_data(path: Path) -> pd.DataFrame:
	"""Load the Excel file into a pandas DataFrame.

	The function will attempt to parse the column named '날짜' as datetimes.
	"""
	df = pd.read_excel(path, engine=None)
	# Normalize column names (strip whitespace)
	df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
	if "날짜" in df.columns:
		df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
	return df


def make_figure(df: pd.DataFrame) -> go.Figure:
	"""Create a Plotly figure with the requested series.

	Expected series: '지수', '외국인', '개인', '기관종합'
	If any of those columns are missing, they are skipped.
	"""
	fig = go.Figure()
	x = df.get("날짜")
	# Put '지수' on the left y-axis and the other three series on a right-side
	# secondary y-axis for better scale separation.
	series_names_left = ["지수"]
	series_names_right = ["외국인", "개인", "기관종합"]

	# left axis traces: make '지수' thicker and smooth (spline)
	for name in series_names_left:
		if name in df.columns:
			fig.add_trace(
				go.Scatter(
					x=x,
					y=df[name],
					mode="lines",
					name=name,
					yaxis="y",
					line=dict(width=4, shape="spline", smoothing=1.3),
					connectgaps=True,
				)
			)

	# right axis traces: use accumulated (cumulative sum) values for these series
	for name in series_names_right:
		if name in df.columns:
			# ensure numeric, coerce errors to NaN, then fill NaN with 0 before cumsum
			series = pd.to_numeric(df[name], errors="coerce").fillna(0).cumsum()
			fig.add_trace(
				go.Scatter(
					x=x,
					y=series,
					mode="lines",
					name=f"{name} (누적)",
					yaxis="y2",
					line=dict(width=2.5, shape="spline", smoothing=1.1),
					connectgaps=True,
				)
			)

	fig.update_layout(
		title="시간별/일별 동향",
		xaxis_title="날짜",
		yaxis=dict(title="지수", side="left"),
		yaxis2=dict(title="외국인/개인/기관 (우측)", overlaying="y", side="right"),
		hovermode="x unified",
		height=700,  # larger height for better readability
		legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
		margin=dict(t=80, b=60, l=60, r=80),
	)

	fig.update_xaxes(rangeslider_visible=True)
	return fig


def make_original_figure(df: pd.DataFrame) -> go.Figure:
	"""Create the original (raw) data figure: 지수 (left) and others (right) as-is."""
	fig = go.Figure()
	x = df.get("날짜")
	# left: 지수
	if "지수" in df.columns:
		fig.add_trace(
			go.Scatter(
				x=x,
				y=df["지수"],
				mode="lines",
				name="지수",
				yaxis="y",
				line=dict(width=4, shape="spline", smoothing=1.3),
				connectgaps=True,
			)
		)

	# right: raw 외국인, 개인, 기관종합
	for name in ["외국인", "개인", "기관종합"]:
		if name in df.columns:
			series = pd.to_numeric(df[name], errors="coerce")
			fig.add_trace(
				go.Scatter(
					x=x,
					y=series,
					mode="lines",
					name=name,
					yaxis="y2",
					line=dict(width=2.5, shape="spline", smoothing=1.1, color=SERIES_COLORS[name]),
					connectgaps=True,
				)
			)
	
	fig.update_layout(
		title="원본 데이터 (Raw)",
		xaxis_title="날짜",
		yaxis=dict(title="지수", side="left"),
		yaxis2=dict(title="외국인/개인/기관 (우측)", overlaying="y", side="right"),
		hovermode="x unified",
		height=800,  # taller figure for better visibility
		legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
		margin=dict(t=80, b=60, l=60, r=80)
	)
	fig.update_xaxes(rangeslider_visible=True)
	return fig


def make_accumulated_figure(df: pd.DataFrame) -> go.Figure:
	"""Create the accumulated figure: right-side series are cumulative; 지수 kept as raw for reference."""
	fig = go.Figure()
	x = df.get("날짜")

	# left: 지수 (raw, emphasized)
	if "지수" in df.columns:
		fig.add_trace(
			go.Scatter(
				x=x,
				y=df["지수"],
				mode="lines",
				name="지수",
				yaxis="y",
				line=dict(width=4, shape="spline", smoothing=1.3),
				connectgaps=True,
			)
		)

	# right: accumulated 외국인, 개인, 기관종합
	for name in ["외국인", "개인", "기관종합"]:
		if name in df.columns:
			series = pd.to_numeric(df[name], errors="coerce").fillna(0).cumsum()
			fig.add_trace(
				go.Scatter(
					x=x,
					y=series,
					mode="lines",
					name=f"{name} (누적)",
					yaxis="y2",
					line=dict(width=2.5, shape="spline", smoothing=1.1, color=SERIES_COLORS[name]),
					connectgaps=True,
				)
			)

	fig.update_layout(
		title="누적 값 (Accumulated)",
		xaxis_title="날짜",
		yaxis=dict(title="지수", side="left"),
		yaxis2=dict(title="외국인/개인/기관 (누적, 우측)", overlaying="y", side="right"),
		hovermode="x unified",
		height=800,  # taller figure for better visibility
		legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
		margin=dict(t=80, b=60, l=60, r=80),
	)
	fig.update_xaxes(rangeslider_visible=True)
	return fig


def create_app(data_path: Path) -> Dash:
	df = load_data(data_path)
	# Get min/max dates for the date range selector
	min_date = df["날짜"].min().date()
	max_date = df["날짜"].max().date()
	
	fig_raw = make_original_figure(df)
	fig_acc = make_accumulated_figure(df)

	app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
	
	# Define callback to update graph date ranges
	@app.callback(
		[Output("raw-graph", "figure"),
		Output("acc-graph", "figure")],
		[Input("start-date", "date"),
		Input("end-date", "date")]
	)
	def update_figures(start_date, end_date):
		if start_date is not None and end_date is not None:
			mask = (df["날짜"].dt.date >= pd.Timestamp(start_date).date()) & \
				   (df["날짜"].dt.date <= pd.Timestamp(end_date).date())
			filtered_df = df[mask]
		else:
			filtered_df = df
		
		return make_original_figure(filtered_df), make_accumulated_figure(filtered_df)

	# Calculate some preset ranges
	today = pd.Timestamp.now().date()
	date_presets = {
		"all": {"label": "전체 기간", "days": None},
		"7d": {"label": "최근 7일", "days": 7},
		"30d": {"label": "최근 30일", "days": 30},
		"90d": {"label": "최근 90일", "days": 90},
		"1y": {"label": "최근 1년", "days": 365},
		"2y": {"label": "최근 2년", "days": 730},
		"3y": {"label": "최근 3년", "days": 1095},
		"4y": {"label": "최근 4년", "days": 1460},
		"5y": {"label": "최근 5년", "days": 1825},
		"10y": {"label": "최근 10년", "days": 3650}
	}

	@app.callback(
		[Output("start-date", "date"),
		Output("end-date", "date")],
		Input("date-preset", "value")
	)
	def update_date_range(preset):
		if preset not in date_presets:
			return no_update, no_update
			
		preset_info = date_presets[preset]
		if preset_info["days"] is None:  # "all" case
			return min_date.isoformat(), max_date.isoformat()
		
		days = preset_info["days"]
		start = max((today - pd.Timedelta(days=days)), min_date)
		return start.isoformat(), today.isoformat()

	app.layout = dbc.Container([
		html.H2("시간별/일별 동향 (Raw vs Accumulated)", className="text-center my-4"),
		dbc.Card([
			dbc.CardBody([
				dbc.Row([
					dbc.Col([
						dbc.Label("빠른 선택:", className="me-2"),
						dcc.Dropdown(
							id="date-preset",
							options=[{'label': v['label'], 'value': k} for k, v in date_presets.items()],
							value="all",
							style={"width": "200px"},
							clearable=False
						)
					], width="auto", className="me-4"),
					dbc.Col([
						dbc.Label("시작일:", className="me-2"),
						dcc.DatePickerSingle(
							id="start-date",
							min_date_allowed=min_date,
							max_date_allowed=max_date,
							date=min_date,
							display_format="YYYY-MM-DD",
							className="me-4",
							day_size=35
						)
					], width="auto"),
					dbc.Col([
						dbc.Label("종료일:", className="me-2"),
						dcc.DatePickerSingle(
							id="end-date",
							min_date_allowed=min_date,
							max_date_allowed=max_date,
							date=max_date,
							display_format="YYYY-MM-DD",
							day_size=35
						)
					], width="auto"),
				], justify="center", align="center"),
			])
		], className="mb-4"),
		dbc.Card([
			dbc.CardBody([
				dcc.Graph(id="raw-graph", figure=fig_raw),
			])
		], className="mb-4"),
		dbc.Card([
			dbc.CardBody([
				dcc.Graph(id="acc-graph", figure=fig_acc),
			])
		], className="mb-4"),
		dbc.Card([
			dbc.CardBody([
				dbc.Row([
					dbc.Col(html.P(f"데이터 행 수: {len(df)}", className="mb-0"), width="auto"),
					dbc.Col(html.P(f"컬럼: {', '.join(map(str, df.columns.tolist()))}", className="mb-0"), width="auto"),
				], justify="center")
			])
		], className="mb-4"),
	], fluid=True)
	return app


def main():
	base = Path(__file__).parent
	data_file = base / "data" / EXCEL_FILENAME
	if not data_file.exists():
		print(f"Excel file not found: {data_file}")
		sys.exit(1)

	app = create_app(data_file)
	# Default port 8050; bind to 127.0.0.1
	app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
	main()

