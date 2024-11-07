use segura;

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
id_dispositivo int auto_increment,
nome varchar(70) not null,
id_modelo int,
mac_address varchar(30) not null,
id_grupo int,
ip varchar(70) not null,
primary key(id_dispositivo),
foreign key(id_modelo) references modelo(id_modelo) ON DELETE SET NULL,
foreign key(id_grupo) references grupo(id_grupo) ON DELETE SET NULL
);