
CREATE TABLE prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    price DECIMAL(10,4),
    timestamp DATETIME,
    INDEX(symbol, timestamp)
);

CREATE TABLE signals (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    type VARCHAR(50),
    value DECIMAL(10,4),
    message TEXT,
    created_at DATETIME
);