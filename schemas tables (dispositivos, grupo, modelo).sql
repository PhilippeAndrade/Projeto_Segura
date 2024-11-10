use segura;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS modelo (
id_modelo int auto_increment,
nome varchar(70) not null,
fabricante varchar(50) not null,
primary key(id_modelo)
);


CREATE TABLE IF NOT EXISTS grupo (
id_grupo int auto_increment,
nome varchar(70) not null,
primary key(id_grupo)
);




CREATE TABLE IF NOT EXISTS dispositivos (
    id_dispositivo INT AUTO_INCREMENT,
    nome VARCHAR(70) NOT NULL,
    id_modelo INT,
    mac_address VARCHAR(30) NOT NULL,
    id_grupo INT,
    ip VARCHAR(70) NOT NULL,
    access_type ENUM('user_password', 'password_only') DEFAULT 'user_password',
    username VARCHAR(50) NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_dispositivo),
    FOREIGN KEY (id_modelo) REFERENCES modelo(id_modelo) ON DELETE SET NULL,
    FOREIGN KEY (id_grupo) REFERENCES grupo(id_grupo) ON DELETE SET NULL
);