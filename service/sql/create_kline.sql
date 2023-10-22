CREATE TABLE kline (
    id BIGSERIAL PRIMARY KEY,
    create_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    symbol VARCHAR(30) NOT NULL,
    interval INT NOT NULL,
    open_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    CONSTRAINT kline_uk UNIQUE (symbol, interval, open_time)
);

CREATE INDEX kline_symbol_timeframe_idx ON kline (symbol, interval);
CREATE INDEX kline_open_time_idx ON kline (open_time);
