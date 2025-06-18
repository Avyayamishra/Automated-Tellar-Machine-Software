#MySQL table schematics
create table if not exists accounts(<br>
    acno int Auto_increment primary key,<br>
    name varchar(255),<br>
    balance int,<br>
    pin int<br>
);<br>
<br>
create table if not exists trans_log(<br>
    trxn_id int auto_increment primary key,<br>
    account int,<br>
    amount int,<br>
    debit int,<br>
    credit int,<br>
    time timestamp default current_timestamp<br>
);<br>