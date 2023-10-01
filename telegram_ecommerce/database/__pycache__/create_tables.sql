

CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY,
    username VARCHAR(150) NOT NULL,
    terms BOOLEAN NOT NULL DEFAULT FALSE,
    is_creator BOOLEAN NOT NULL DEFAULT FALSE
) engine=MyISAM;


CREATE TABLE IF NOT EXISTS photo (
    id VARCHAR(200) PRIMARY KEY,
    image_blob BLOB DEFAULT NULL
) engine=MyISAM;


CREATE TABLE IF NOT EXISTS efiles (
    id VARCHAR(200) PRIMARY KEY,
    efile_blob LONGBLOB DEFAULT NULL
) engine=MyISAM;


CREATE TABLE IF NOT EXISTS category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    creator_id INT NOT NULL,
    description VARCHAR(2000) NOT NULL
) engine=MyISAM;


CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(150) NOT NULL,
    creator_id INT NOT NULL,
    description VARCHAR(2000) NOT NULL,
    price INT NOT NULL,
    sale_price INT NOT NULL,
    in_stock INT NOT NULL,
    total_sold INT NOT NULL,
    category_id INT NOT NULL,
    image_id VARCHAR(200),
    FOREIGN KEY (image_id)
    REFERENCES photo (id),
    FOREIGN KEY (category_id)
    REFERENCES category (id),
    efile_id VARCHAR(200),
    FOREIGN KEY (efile_id)
    REFERENCES efiles (id),
    digital BOOLEAN NOT NULL DEFAULT FALSE,
    shippable BOOLEAN NOT NULL DEFAULT FALSE,
    FULLTEXT(name, description)
) engine=MyISAM;


CREATE TABLE IF NOT EXISTS receipts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL,
    date VARCHAR(50) NOT NULL,
    creator_id INT NOT NULL,
    buyer_id INT NOT NULL,
    currency VARCHAR(10) NOT NULL,
    price INT NOT NULL,
    tip INT NOT NULL,
    total_paid INT NOT NULL,
    product_id INT NOT NULL,
    successful_payment VARCHAR(300) NOT NULL,
    FOREIGN KEY (buyer_id)
    REFERENCES customers (id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,
    FOREIGN KEY (creator_id)
    REFERENCES category (creator_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,
    FOREIGN KEY (product_id)
    REFERENCES products (id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
) engine=MyISAM;


SET GLOBAL wait_timeout = 1728000 ;

