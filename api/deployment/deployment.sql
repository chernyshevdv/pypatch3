CREATE TABLE deployment (
    id INTEGER PRIMARY KEY,
    title TEXT UNIQUE,
    excel_columns TEXT,
    excel_header_row INTEGER NOT NULL DEFAULT  0
);

CREATE TABLE cycle (
    id INTEGER PRIMARY KEY,
    deployment_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    started DATETIME,
    rag char,
    status_update TEXT,
    is_active BOOLEAN,
    excel_columns TEXT,
    excel_header_row INTEGER,
    FOREIGN KEY (deployment_id) REFERENCES deployment(id) ON DELETE CASCADE
);

CREATE TABLE report (
    id INTEGER PRIMARY KEY,
    cycle_id INTEGER NOT NULL,
    udpated DATETIME NOT NULL,
    show_in_history TEXT(3) NOT NULL DEFAULT 'yes',
    FOREIGN KEY (cycle_id) REFERENCES cycle (id) ON DELETE CASCADE
);