const spec = {
  $schema: 'https://vega.github.io/schema/vega-lite/v4.json',
  width: 600,
  height: 400,
  padding: 5,

  data: { url: 'daily_prices.csv' },
  mark: {
    type: 'line',
    interpolate: 'monotone'
  },
  encoding: {
    x: { field: 'date', type: 'temporal' },
    y: { field: 'price', type: 'quantitative' }
  }
};
