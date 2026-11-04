BEGIN TRANSACTION;
CREATE TABLE colaboradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                numero TEXT NOT NULL,
                cargo TEXT NOT NULL CHECK(cargo IN ('caixa', 'gerente')),
                primeiro_acesso INTEGER NOT NULL DEFAULT 1 CHECK(primeiro_acesso IN (0, 1)),
                ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0, 1)),
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );
INSERT INTO "colaboradores" VALUES(1,'Gerente Administrador','gerente@churrascontrol.com','8e3e65f14ff20bb4ec5220027905acb1d31a5d1707ce611834e6d0a1bef0e102','(31) 99999-9999','gerente',1,1,'2026-10-06T09:49:55.633647','2026-10-06T09:49:55.633647');
INSERT INTO "colaboradores" VALUES(5,'Operador Caixa Teste','caixa_teste_automated@churrascontrol.com','62367f94eee70bed09e3804a8604ca24aacc951d31bb2ff59a6600923973e75d','(11) 98765-4321','caixa',1,1,'2026-10-06T10:03:42.973468','2026-10-06T10:03:42.973468');
CREATE TABLE comandas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER,
                numero_mesa_historico INTEGER NOT NULL,
                data_abertura TEXT NOT NULL,
                data_fechamento TEXT,
                status TEXT DEFAULT 'ABERTA',
                taxa_servico INTEGER DEFAULT 1,
                qtd_pessoas INTEGER DEFAULT 1,
                valor_total REAL DEFAULT 0.0,
                FOREIGN KEY(mesa_id) REFERENCES mesas(id) ON DELETE SET NULL
            );
INSERT INTO "comandas" VALUES(2,NULL,55,'2026-08-25T11:27:15.842060',NULL,'CANCELADA',1,1,0.0);
INSERT INTO "comandas" VALUES(3,NULL,2,'2026-08-26T18:44:10.704256','2026-08-26T20:43:25.171199','PAGA',0,1,370.0);
INSERT INTO "comandas" VALUES(4,NULL,1,'2026-09-22T10:30:35.324199',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(5,NULL,3,'2026-09-22T10:30:55.109145','2026-09-28T13:24:07.155559','PAGA',1,2,85.21);
INSERT INTO "comandas" VALUES(6,NULL,1,'2026-09-28T10:46:33.053653',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(7,NULL,2,'2026-09-28T10:50:52.442196',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(8,NULL,999,'2026-09-29T14:42:57.279519','2026-09-29T14:42:57.288600','PAGA',1,3,96.69);
INSERT INTO "comandas" VALUES(11,NULL,999,'2026-09-30T11:46:06.407644','2026-09-30T11:46:06.425722','PAGA',1,3,96.69);
INSERT INTO "comandas" VALUES(13,NULL,999,'2026-09-30T11:51:36.692521','2026-09-30T11:51:36.703117','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(15,NULL,999,'2026-09-30T11:53:37.434854','2026-09-30T11:53:37.446753','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(17,NULL,999,'2026-09-30T11:55:46.800943','2026-09-30T11:55:46.811478','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(19,NULL,999,'2026-09-30T12:19:11.006699','2026-09-30T12:19:11.048488','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(21,NULL,999,'2026-09-30T12:21:24.108469','2026-09-30T12:21:24.151572','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(22,NULL,99,'2026-09-30T14:07:05.295252',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(23,NULL,8,'2026-09-30T14:07:05.340829',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(24,NULL,99,'2026-09-30T14:07:36.335454',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(25,NULL,8,'2026-09-30T14:07:36.394051',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(26,NULL,1,'2026-09-30T14:14:32.713755',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(27,NULL,99,'2026-09-30T14:18:41.548752',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(28,NULL,8,'2026-09-30T14:18:41.617850',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(29,NULL,99,'2026-09-30T14:24:06.603737',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(30,NULL,8,'2026-09-30T14:24:06.676197',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(31,NULL,1,'2026-09-30T14:27:49.366301',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(32,NULL,99,'2026-09-30T14:47:59.738626',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(33,NULL,8,'2026-09-30T14:47:59.820725',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(34,NULL,99,'2026-09-30T14:55:13.804435',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(35,NULL,8,'2026-09-30T14:55:13.871705',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(36,35,1,'2026-09-30T14:58:14.647306',NULL,'ABERTA',1,2,0.0);
INSERT INTO "comandas" VALUES(37,NULL,99,'2026-09-30T14:58:54.007048',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(38,NULL,8,'2026-09-30T14:58:54.073924',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(39,NULL,2,'2026-09-30T14:59:28.793385',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(40,NULL,99,'2026-09-30T15:02:14.910420',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(41,NULL,8,'2026-09-30T15:02:15.052312',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(42,NULL,99,'2026-09-30T15:13:55.729015',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(43,NULL,8,'2026-09-30T15:13:55.793778',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(44,NULL,99,'2026-09-30T15:28:39.332973',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(45,NULL,8,'2026-09-30T15:28:39.350354',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(46,NULL,99,'2026-09-30T15:34:18.227791',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(47,NULL,8,'2026-09-30T15:34:18.289900',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(48,NULL,999,'2026-10-01T09:48:02.906563','2026-10-01T09:48:02.925910','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(50,NULL,99,'2026-10-01T09:48:09.362465',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(51,NULL,8,'2026-10-01T09:48:09.377879',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(52,NULL,999,'2026-10-01T09:51:41.542626','2026-10-01T09:51:41.561033','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(54,NULL,99,'2026-10-01T09:51:43.694681',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(55,NULL,8,'2026-10-01T09:51:43.733451',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(56,NULL,999,'2026-10-01T10:00:02.658585','2026-10-01T10:00:02.673760','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(58,NULL,99,'2026-10-01T10:00:04.685012',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(59,NULL,8,'2026-10-01T10:00:04.712945',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(60,NULL,999,'2026-10-01T10:02:03.868226','2026-10-01T10:02:03.881126','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(62,NULL,99,'2026-10-01T10:02:05.477504',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(63,NULL,8,'2026-10-01T10:02:05.521441',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(64,NULL,999,'2026-10-01T10:27:56.771622','2026-10-01T10:27:56.824340','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(66,NULL,99,'2026-10-01T10:27:58.735508',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(67,NULL,8,'2026-10-01T10:27:58.832921',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(68,NULL,999,'2026-10-01T10:30:38.105799','2026-10-01T10:30:38.159575','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(70,NULL,99,'2026-10-01T10:30:40.161516',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(71,NULL,8,'2026-10-01T10:30:40.285383',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(72,NULL,999,'2026-10-01T10:50:59.629301','2026-10-01T10:50:59.665399','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(74,NULL,99,'2026-10-01T10:51:01.647827',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(75,NULL,8,'2026-10-01T10:51:01.749847',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(76,NULL,999,'2026-10-01T11:01:35.326590','2026-10-01T11:01:35.351843','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(78,NULL,99,'2026-10-01T11:01:37.281039',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(79,NULL,8,'2026-10-01T11:01:37.362072',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(80,NULL,999,'2026-10-01T11:13:32.119883','2026-10-01T11:13:32.146202','PAGA',1,3,36.0);
INSERT INTO "comandas" VALUES(82,NULL,99,'2026-10-01T11:13:33.862638',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(83,NULL,8,'2026-10-01T11:13:33.918926',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(84,NULL,999,'2026-10-01T11:28:01.649945','2026-10-01T11:28:01.674508','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(86,NULL,99,'2026-10-01T11:28:03.466882',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(87,NULL,8,'2026-10-01T11:28:03.549270',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(88,NULL,999,'2026-10-01T12:09:21.181760','2026-10-01T12:09:21.203018','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(90,NULL,99,'2026-10-01T12:09:23.158450',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(91,NULL,8,'2026-10-01T12:09:23.226110',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(92,NULL,999,'2026-10-01T12:17:18.795744','2026-10-01T12:17:18.821841','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(94,NULL,99,'2026-10-01T12:17:20.257312',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(95,NULL,8,'2026-10-01T12:17:20.310476',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(96,NULL,999,'2026-10-02T10:32:04.760095','2026-10-02T10:32:04.771452','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(98,NULL,99,'2026-10-02T10:32:06.744629',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(99,NULL,8,'2026-10-02T10:32:06.765822',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(100,NULL,999,'2026-10-02T10:40:29.590734','2026-10-02T10:40:29.601727','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(102,NULL,99,'2026-10-02T10:40:34.358977',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(103,NULL,8,'2026-10-02T10:40:34.402881',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(104,NULL,999,'2026-10-02T11:34:27.781521','2026-10-02T11:34:27.789285','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(106,NULL,99,'2026-10-02T11:34:32.059625',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(107,NULL,8,'2026-10-02T11:34:32.093971',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(108,NULL,999,'2026-10-02T11:37:30.317396','2026-10-02T11:37:30.326805','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(110,NULL,99,'2026-10-02T11:37:34.767454',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(111,NULL,8,'2026-10-02T11:37:34.792422',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(112,NULL,999,'2026-10-05T21:24:28.413338','2026-10-05T21:24:28.419379','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(114,NULL,99,'2026-10-05T21:24:32.244868',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(115,NULL,8,'2026-10-05T21:24:32.274892',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(116,NULL,999,'2026-10-06T09:39:30.357277','2026-10-06T09:39:30.363362','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(118,NULL,99,'2026-10-06T09:39:34.749725',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(119,NULL,8,'2026-10-06T09:39:34.777647',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(120,NULL,999,'2026-10-06T09:59:06.932273','2026-10-06T09:59:06.939906','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(122,NULL,99,'2026-10-06T09:59:11.557885',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(123,NULL,8,'2026-10-06T09:59:11.571687',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(124,NULL,999,'2026-10-06T10:00:14.624331','2026-10-06T10:00:14.632168','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(126,NULL,99,'2026-10-06T10:00:19.119805',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(127,NULL,8,'2026-10-06T10:00:19.138978',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(128,NULL,999,'2026-10-06T10:03:37.315560','2026-10-06T10:03:37.325817','PAGA',1,3,33.0);
INSERT INTO "comandas" VALUES(129,NULL,888,'2026-10-06T10:03:38.824747','2026-10-06T10:03:38.829942','PAGA',0,2,10.0);
INSERT INTO "comandas" VALUES(130,NULL,99,'2026-10-06T10:03:41.553995',NULL,'CANCELADA',1,2,0.0);
INSERT INTO "comandas" VALUES(131,NULL,8,'2026-10-06T10:03:41.566820',NULL,'CANCELADA',1,2,0.0);
CREATE TABLE fila_sincronizacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metodo TEXT NOT NULL,
                rota TEXT NOT NULL,
                payload_json TEXT,
                status TEXT DEFAULT 'PENDENTE',
                tentativas INTEGER DEFAULT 0,
                criado_em TEXT NOT NULL,
                processado_em TEXT
            , ultimo_erro TEXT);
INSERT INTO "fila_sincronizacao" VALUES(1,'POST','/comandas/8/itens','{"produto_query": "Tutu à Mineira", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-29T14:42:57.282867','2026-09-29T14:58:25.476352',NULL);
INSERT INTO "fila_sincronizacao" VALUES(2,'POST','/comandas/8/itens','{"produto_query": "Tutu à Mineira", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-29T14:42:57.285948','2026-09-29T14:58:29.025307',NULL);
INSERT INTO "fila_sincronizacao" VALUES(6,'POST','/comandas/11/itens','{"produto_query": "Tutu à Mineira", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-30T11:46:06.414335','2026-09-30T12:09:27.592776',NULL);
INSERT INTO "fila_sincronizacao" VALUES(7,'POST','/comandas/11/itens','{"produto_query": "Tutu à Mineira", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T11:46:06.421831','2026-09-30T12:09:30.824652',NULL);
INSERT INTO "fila_sincronizacao" VALUES(9,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:51:36.274367','2026-09-30T12:09:50.700597',NULL);
INSERT INTO "fila_sincronizacao" VALUES(12,'POST','/comandas/13/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-30T11:51:36.697044','2026-09-30T12:10:26.402345',NULL);
INSERT INTO "fila_sincronizacao" VALUES(13,'POST','/comandas/13/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T11:51:36.700157','2026-09-30T12:10:29.669221',NULL);
INSERT INTO "fila_sincronizacao" VALUES(15,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:53:37.025314','2026-09-30T12:10:48.898647',NULL);
INSERT INTO "fila_sincronizacao" VALUES(18,'POST','/comandas/15/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-30T11:53:37.439899','2026-09-30T12:11:24.312802',NULL);
INSERT INTO "fila_sincronizacao" VALUES(19,'POST','/comandas/15/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T11:53:37.443823','2026-09-30T12:11:27.565683',NULL);
INSERT INTO "fila_sincronizacao" VALUES(21,'POST','/produto','{"codigo_pdv": "9999", "nome": "Picanha Teste Especial", "categoria": "Carnes", "preco": 89.9, "descricao": "Picanha nobre maturada grelhada na brasa.", "url_imagem": "https://images.unsplash.com/photo-teste", "qtd_disp": 12, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:53:55.227662','2026-09-30T12:11:46.839502',NULL);
INSERT INTO "fila_sincronizacao" VALUES(24,'POST','/produto','{"codigo_pdv": "8888", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:54:53.265816','2026-09-30T12:12:22.308971',NULL);
INSERT INTO "fila_sincronizacao" VALUES(26,'POST','/produto','{"codigo_pdv": "7777", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:55:37.372799','2026-09-30T12:12:41.506733',NULL);
INSERT INTO "fila_sincronizacao" VALUES(29,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:55:46.367258','2026-09-30T12:13:17.054682',NULL);
INSERT INTO "fila_sincronizacao" VALUES(32,'POST','/comandas/17/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-30T11:55:46.805230','2026-09-30T12:13:52.435730',NULL);
INSERT INTO "fila_sincronizacao" VALUES(33,'POST','/comandas/17/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T11:55:46.808986','2026-09-30T12:13:55.966281',NULL);
INSERT INTO "fila_sincronizacao" VALUES(35,'POST','/produto','{"codigo_pdv": "8888", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:55:47.264330','2026-09-30T12:14:15.194090',NULL);
INSERT INTO "fila_sincronizacao" VALUES(37,'POST','/produto','{"codigo_pdv": "7777", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T11:55:47.636540','2026-09-30T12:14:38.675098',NULL);
INSERT INTO "fila_sincronizacao" VALUES(40,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:19:10.420469','2026-09-30T12:19:11.749945',NULL);
INSERT INTO "fila_sincronizacao" VALUES(43,'POST','/comandas/19/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-30T12:19:11.019312','2026-09-30T12:19:47.494520',NULL);
INSERT INTO "fila_sincronizacao" VALUES(44,'POST','/comandas/19/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T12:19:11.038439','2026-09-30T12:19:50.691345',NULL);
INSERT INTO "fila_sincronizacao" VALUES(46,'POST','/produto','{"codigo_pdv": "T81669", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:21:09.228514','2026-09-30T12:21:10.041725',NULL);
INSERT INTO "fila_sincronizacao" VALUES(49,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:21:15.897798','2026-09-30T12:21:45.686818',NULL);
INSERT INTO "fila_sincronizacao" VALUES(52,'POST','/comandas/21/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-09-30T12:21:24.126269','2026-09-30T12:22:21.107775',NULL);
INSERT INTO "fila_sincronizacao" VALUES(53,'POST','/comandas/21/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T12:21:24.142085','2026-09-30T12:22:24.226979',NULL);
INSERT INTO "fila_sincronizacao" VALUES(55,'POST','/produto','{"codigo_pdv": "T81691", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:21:31.821935','2026-09-30T12:22:43.790947',NULL);
INSERT INTO "fila_sincronizacao" VALUES(57,'POST','/produto','{"codigo_pdv": "T82271", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:31:11.888744','2026-09-30T12:31:13.406116',NULL);
INSERT INTO "fila_sincronizacao" VALUES(59,'POST','/produto','{"codigo_pdv": "T82287", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:31:27.495011','2026-09-30T12:31:33.091180',NULL);
INSERT INTO "fila_sincronizacao" VALUES(62,'POST','/produto','{"codigo_pdv": "T82710", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:38:30.449588','2026-09-30T12:38:31.481397',NULL);
INSERT INTO "fila_sincronizacao" VALUES(64,'POST','/produto','{"codigo_pdv": "T82724", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:38:44.595703','2026-09-30T12:38:50.878268',NULL);
INSERT INTO "fila_sincronizacao" VALUES(67,'POST','/produto','{"codigo_pdv": "T83177", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:46:17.088826','2026-09-30T12:47:46.126612',NULL);
INSERT INTO "fila_sincronizacao" VALUES(69,'POST','/produto','{"codigo_pdv": "T83189", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:46:29.857143','2026-09-30T12:48:05.205855',NULL);
INSERT INTO "fila_sincronizacao" VALUES(72,'POST','/produto','{"codigo_pdv": "T83355", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T12:49:15.390363','2026-09-30T12:49:17.001797',NULL);
INSERT INTO "fila_sincronizacao" VALUES(74,'POST','/produto','{"codigo_pdv": "T86545", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T13:42:25.127725','2026-09-30T13:42:26.768141',NULL);
INSERT INTO "fila_sincronizacao" VALUES(76,'POST','/produto','{"codigo_pdv": "T86593", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T13:43:13.193930','2026-09-30T13:43:14.732966',NULL);
INSERT INTO "fila_sincronizacao" VALUES(79,'POST','/produto','{"codigo_pdv": "T87006", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T13:50:06.201474','2026-09-30T13:50:07.304133',NULL);
INSERT INTO "fila_sincronizacao" VALUES(84,'POST','/produto','{"codigo_pdv": "T87156", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T13:52:36.054423','2026-09-30T14:10:33.924247',NULL);
INSERT INTO "fila_sincronizacao" VALUES(86,'POST','/produto','{"codigo_pdv": "T87156", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T13:52:36.596100','2026-09-30T14:10:53.126194',NULL);
INSERT INTO "fila_sincronizacao" VALUES(89,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:07:05.288361','2026-09-30T14:11:28.576978',NULL);
INSERT INTO "fila_sincronizacao" VALUES(90,'POST','/comandas/22/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T14:07:05.307535','2026-09-30T14:11:31.867305',NULL);
INSERT INTO "fila_sincronizacao" VALUES(91,'DELETE','/itens_comanda/15','{}','ENVIADO',0,'2026-09-30T14:07:05.321306','2026-09-30T14:11:35.040877',NULL);
INSERT INTO "fila_sincronizacao" VALUES(93,'POST','/comandas/23/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-09-30T14:07:05.345091','2026-09-30T14:11:54.155584',NULL);
INSERT INTO "fila_sincronizacao" VALUES(94,'POST','/comandas/23/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-09-30T14:07:05.347040','2026-09-30T14:11:57.444814',NULL);
INSERT INTO "fila_sincronizacao" VALUES(95,'POST','/produto','{"codigo_pdv": "T88055", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:07:35.091983','2026-09-30T14:12:00.934826',NULL);
INSERT INTO "fila_sincronizacao" VALUES(97,'POST','/produto','{"codigo_pdv": "T88055", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:07:35.677859','2026-09-30T14:12:20.152442',NULL);
INSERT INTO "fila_sincronizacao" VALUES(100,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:07:36.330639','2026-09-30T14:12:55.136097',NULL);
INSERT INTO "fila_sincronizacao" VALUES(101,'POST','/comandas/24/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T14:07:36.346633','2026-09-30T14:12:58.393784',NULL);
INSERT INTO "fila_sincronizacao" VALUES(102,'DELETE','/itens_comanda/18','{}','ENVIADO',0,'2026-09-30T14:07:36.371593','2026-09-30T14:13:01.574335',NULL);
INSERT INTO "fila_sincronizacao" VALUES(104,'POST','/comandas/25/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-09-30T14:07:36.397401','2026-09-30T14:13:21.387067',NULL);
INSERT INTO "fila_sincronizacao" VALUES(105,'POST','/comandas/25/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-09-30T14:07:36.399798','2026-09-30T14:13:24.672607',NULL);
INSERT INTO "fila_sincronizacao" VALUES(106,'POST','/comandas/26/itens','{"produto_query": "Suco de Goiaba", "quantidade": 5, "observacao": ""}','ENVIADO',0,'2026-09-30T14:14:32.715850','2026-09-30T14:14:33.630986',NULL);
INSERT INTO "fila_sincronizacao" VALUES(107,'POST','/produto','{"codigo_pdv": "T88720", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:18:40.554889','2026-09-30T14:18:42.240442',NULL);
INSERT INTO "fila_sincronizacao" VALUES(109,'POST','/produto','{"codigo_pdv": "T88720", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:18:40.963312','2026-09-30T14:19:01.385088',NULL);
INSERT INTO "fila_sincronizacao" VALUES(112,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:18:41.534002','2026-09-30T14:19:36.935881',NULL);
INSERT INTO "fila_sincronizacao" VALUES(113,'POST','/comandas/27/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T14:18:41.562564','2026-09-30T14:19:40.201761',NULL);
INSERT INTO "fila_sincronizacao" VALUES(114,'DELETE','/itens_comanda/22','{}','ENVIADO',0,'2026-09-30T14:18:41.585109','2026-09-30T14:19:43.332042',NULL);
INSERT INTO "fila_sincronizacao" VALUES(116,'POST','/comandas/28/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-09-30T14:18:41.623953','2026-09-30T14:20:02.517774',NULL);
INSERT INTO "fila_sincronizacao" VALUES(117,'POST','/comandas/28/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-09-30T14:18:41.629598','2026-09-30T14:20:06.198631',NULL);
INSERT INTO "fila_sincronizacao" VALUES(118,'POST','/produto','{"codigo_pdv": "T89045", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:24:05.577605','2026-09-30T14:24:07.186934',NULL);
INSERT INTO "fila_sincronizacao" VALUES(129,'POST','/comandas/31/itens','{"produto_query": "Suco de Goiaba", "quantidade": 4, "observacao": ""}','ENVIADO',0,'2026-09-30T14:27:49.371162','2026-09-30T14:27:50.512928',NULL);
INSERT INTO "fila_sincronizacao" VALUES(130,'POST','/produto','{"codigo_pdv": "T90478", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:47:58.645308','2026-09-30T14:48:01.257750',NULL);
INSERT INTO "fila_sincronizacao" VALUES(141,'POST','/produto','{"codigo_pdv": "T90913", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:55:13.170534','2026-09-30T14:55:14.860734',NULL);
INSERT INTO "fila_sincronizacao" VALUES(149,'POST','/comandas/36/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T14:58:14.649900','2026-09-30T14:58:16.176749',NULL);
INSERT INTO "fila_sincronizacao" VALUES(150,'PATCH','/itens_comanda/35','{"quantidade": 1, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T14:58:22.880923','2026-09-30T14:58:24.311667',NULL);
INSERT INTO "fila_sincronizacao" VALUES(151,'POST','/produto','{"codigo_pdv": "T91133", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T14:58:53.436725','2026-09-30T14:58:55.323069',NULL);
INSERT INTO "fila_sincronizacao" VALUES(160,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T15:02:14.896569','2026-09-30T15:02:16.840802',NULL);
INSERT INTO "fila_sincronizacao" VALUES(161,'POST','/comandas/40/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T15:02:14.930851','2026-09-30T15:02:20.030832',NULL);
INSERT INTO "fila_sincronizacao" VALUES(172,'PATCH','/itens_comanda/35','{"quantidade": 2, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T15:05:30.639024','2026-09-30T15:05:31.556855',NULL);
INSERT INTO "fila_sincronizacao" VALUES(173,'PATCH','/itens_comanda/35','{"quantidade": 3, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T15:05:30.805292','2026-09-30T15:05:34.731010',NULL);
INSERT INTO "fila_sincronizacao" VALUES(176,'PATCH','/itens_comanda/35','{"quantidade": 4, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T15:07:17.961648','2026-09-30T15:07:19.421767',NULL);
INSERT INTO "fila_sincronizacao" VALUES(177,'PATCH','/itens_comanda/35','{"quantidade": 3, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T15:07:18.311959','2026-09-30T15:07:22.547608',NULL);
INSERT INTO "fila_sincronizacao" VALUES(178,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T15:13:55.719870','2026-09-30T15:13:57.200647',NULL);
INSERT INTO "fila_sincronizacao" VALUES(179,'POST','/comandas/42/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T15:13:55.740567','2026-09-30T15:14:00.678991',NULL);
INSERT INTO "fila_sincronizacao" VALUES(190,'PATCH','/produto/50','{"codigo_pdv": "T81669", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Prato especial preparado com ingredientes selecionados, tempero autêntico da casa e finalização primorosa.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80", "qtd_disp": 10, "precisa_produzir": false, "disponivel": true}','ENVIADO',0,'2026-09-30T15:17:05.477044','2026-09-30T15:17:06.819432',NULL);
INSERT INTO "fila_sincronizacao" VALUES(191,'POST','/comandas/36/itens','{"produto_query": "Ancho Especial Parrilla", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-09-30T15:18:20.777961','2026-09-30T15:18:22.285534',NULL);
INSERT INTO "fila_sincronizacao" VALUES(192,'PATCH','/itens_comanda/35','{"quantidade": 5, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T15:18:54.089547','2026-09-30T15:18:55.423026',NULL);
INSERT INTO "fila_sincronizacao" VALUES(193,'PATCH','/itens_comanda/35','{"quantidade": 4, "preco_momento": 11.0, "observacao": ""}','ENVIADO',0,'2026-09-30T15:18:54.305913','2026-09-30T15:18:58.580348',NULL);
INSERT INTO "fila_sincronizacao" VALUES(198,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T15:28:39.328830','2026-09-30T15:31:35.160950',NULL);
INSERT INTO "fila_sincronizacao" VALUES(199,'POST','/comandas/44/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T15:28:39.336881','2026-09-30T15:31:38.459762',NULL);
INSERT INTO "fila_sincronizacao" VALUES(201,'DELETE','/produto/90','{}','ENVIADO',0,'2026-09-30T15:28:39.346798','2026-09-30T15:31:57.631295',NULL);
INSERT INTO "fila_sincronizacao" VALUES(202,'POST','/comandas/45/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-09-30T15:28:39.351905','2026-09-30T15:32:00.889148',NULL);
INSERT INTO "fila_sincronizacao" VALUES(203,'POST','/comandas/45/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-09-30T15:28:39.353365','2026-09-30T15:32:04.162252',NULL);
INSERT INTO "fila_sincronizacao" VALUES(204,'POST','/produto','{"codigo_pdv": "T92930", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T15:28:50.961598','2026-09-30T15:32:07.373979',NULL);
INSERT INTO "fila_sincronizacao" VALUES(205,'PATCH','/produto/91','{"codigo_pdv": "T92930", "nome": "Ancho Especial Parrilla (Atualizado)", "categoria": "Carnes", "preco": 89.0, "descricao": "Descricao atualizada para teste.", "url_imagem": "https://images.unsplash.com/photo-atualizada", "qtd_disp": 5, "precisa_produzir": false, "disponivel": false}','ENVIADO',0,'2026-09-30T15:28:50.965946','2026-09-30T15:32:10.549336',NULL);
INSERT INTO "fila_sincronizacao" VALUES(206,'DELETE','/produto/91','{}','ENVIADO',0,'2026-09-30T15:28:50.970831','2026-09-30T15:32:13.762882',NULL);
INSERT INTO "fila_sincronizacao" VALUES(207,'POST','/produto','{"codigo_pdv": "T92950", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T15:29:10.612880','2026-09-30T15:32:17.186509',NULL);
INSERT INTO "fila_sincronizacao" VALUES(208,'DELETE','/produto/92','{}','ENVIADO',0,'2026-09-30T15:29:10.617898','2026-09-30T15:32:20.369330',NULL);
INSERT INTO "fila_sincronizacao" VALUES(209,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-09-30T15:34:18.218905','2026-09-30T15:34:19.450262',NULL);
INSERT INTO "fila_sincronizacao" VALUES(210,'POST','/comandas/46/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-09-30T15:34:18.237081','2026-09-30T15:34:22.815309',NULL);
INSERT INTO "fila_sincronizacao" VALUES(212,'DELETE','/produto/93','{}','ENVIADO',0,'2026-09-30T15:34:18.276528','2026-09-30T15:34:42.403456',NULL);
INSERT INTO "fila_sincronizacao" VALUES(213,'POST','/comandas/47/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-09-30T15:34:18.296208','2026-09-30T15:34:45.924841',NULL);
INSERT INTO "fila_sincronizacao" VALUES(214,'POST','/comandas/47/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-09-30T15:34:18.301194','2026-09-30T15:34:49.156631',NULL);
INSERT INTO "fila_sincronizacao" VALUES(215,'POST','/produto','{"codigo_pdv": "T58880", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:48:00.205961','2026-10-01T10:06:57.921710',NULL);
INSERT INTO "fila_sincronizacao" VALUES(216,'DELETE','/produto/94','{}','ENVIADO',0,'2026-10-01T09:48:00.209691','2026-10-01T10:07:01.107049',NULL);
INSERT INTO "fila_sincronizacao" VALUES(217,'POST','/comandas/48/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T09:48:02.914160','2026-10-01T10:07:04.746178',NULL);
INSERT INTO "fila_sincronizacao" VALUES(218,'POST','/comandas/48/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-10-01T09:48:02.921591','2026-10-01T10:07:08.148049',NULL);
INSERT INTO "fila_sincronizacao" VALUES(220,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:48:07.481574','2026-10-01T10:07:37.394100',NULL);
INSERT INTO "fila_sincronizacao" VALUES(221,'DELETE','/produto/95','{}','ENVIADO',0,'2026-10-01T09:48:07.487171','2026-10-01T10:07:40.574376',NULL);
INSERT INTO "fila_sincronizacao" VALUES(223,'POST','/produto','{"codigo_pdv": "T58888", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:48:08.129559','2026-10-01T10:08:02.076593',NULL);
INSERT INTO "fila_sincronizacao" VALUES(224,'PATCH','/produto/96','{"codigo_pdv": "T58888", "nome": "Ancho Especial Parrilla (Atualizado)", "categoria": "Carnes", "preco": 89.0, "descricao": "Descricao atualizada para teste.", "url_imagem": "https://images.unsplash.com/photo-atualizada", "qtd_disp": 5, "precisa_produzir": false, "disponivel": false}','ENVIADO',0,'2026-10-01T09:48:08.137870','2026-10-01T10:08:05.260267',NULL);
INSERT INTO "fila_sincronizacao" VALUES(225,'DELETE','/produto/96','{}','ENVIADO',0,'2026-10-01T09:48:08.145177','2026-10-01T10:08:08.850798',NULL);
INSERT INTO "fila_sincronizacao" VALUES(226,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:48:09.354697','2026-10-01T10:08:12.401450',NULL);
INSERT INTO "fila_sincronizacao" VALUES(227,'POST','/comandas/50/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-10-01T09:48:09.365195','2026-10-01T10:08:15.853641',NULL);
INSERT INTO "fila_sincronizacao" VALUES(229,'DELETE','/produto/97','{}','ENVIADO',0,'2026-10-01T09:48:09.374652','2026-10-01T10:08:35.824851',NULL);
INSERT INTO "fila_sincronizacao" VALUES(230,'POST','/comandas/51/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-10-01T09:48:09.379948','2026-10-01T10:08:39.305230',NULL);
INSERT INTO "fila_sincronizacao" VALUES(231,'POST','/comandas/51/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-10-01T09:48:09.381194','2026-10-01T10:08:42.581655',NULL);
INSERT INTO "fila_sincronizacao" VALUES(232,'POST','/produto','{"codigo_pdv": "T59100", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:51:40.892830','2026-10-01T10:08:46.185601',NULL);
INSERT INTO "fila_sincronizacao" VALUES(233,'DELETE','/produto/98','{}','ENVIADO',0,'2026-10-01T09:51:40.900026','2026-10-01T10:08:49.346958',NULL);
INSERT INTO "fila_sincronizacao" VALUES(234,'POST','/comandas/52/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T09:51:41.549976','2026-10-01T10:08:52.622619',NULL);
INSERT INTO "fila_sincronizacao" VALUES(235,'POST','/comandas/52/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-10-01T09:51:41.555752','2026-10-01T10:08:55.828428',NULL);
INSERT INTO "fila_sincronizacao" VALUES(237,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:51:42.229942','2026-10-01T10:09:16.660210',NULL);
INSERT INTO "fila_sincronizacao" VALUES(238,'DELETE','/produto/99','{}','ENVIADO',0,'2026-10-01T09:51:42.235125','2026-10-01T10:09:19.882944',NULL);
INSERT INTO "fila_sincronizacao" VALUES(240,'POST','/produto','{"codigo_pdv": "T59102", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:51:42.886378','2026-10-01T10:09:38.821742',NULL);
INSERT INTO "fila_sincronizacao" VALUES(241,'PATCH','/produto/100','{"codigo_pdv": "T59102", "nome": "Ancho Especial Parrilla (Atualizado)", "categoria": "Carnes", "preco": 89.0, "descricao": "Descricao atualizada para teste.", "url_imagem": "https://images.unsplash.com/photo-atualizada", "qtd_disp": 5, "precisa_produzir": false, "disponivel": false}','ENVIADO',0,'2026-10-01T09:51:42.895381','2026-10-01T10:09:42.006476',NULL);
INSERT INTO "fila_sincronizacao" VALUES(242,'DELETE','/produto/100','{}','ENVIADO',0,'2026-10-01T09:51:42.903487','2026-10-01T10:09:45.174083',NULL);
INSERT INTO "fila_sincronizacao" VALUES(243,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T09:51:43.689470','2026-10-01T10:09:48.389970',NULL);
INSERT INTO "fila_sincronizacao" VALUES(244,'POST','/comandas/54/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-10-01T09:51:43.702435','2026-10-01T10:09:51.667695',NULL);
INSERT INTO "fila_sincronizacao" VALUES(246,'DELETE','/produto/101','{}','ENVIADO',0,'2026-10-01T09:51:43.723294','2026-10-01T10:10:10.772214',NULL);
INSERT INTO "fila_sincronizacao" VALUES(247,'POST','/comandas/55/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-10-01T09:51:43.737376','2026-10-01T10:10:14.083830',NULL);
INSERT INTO "fila_sincronizacao" VALUES(248,'POST','/comandas/55/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-10-01T09:51:43.739347','2026-10-01T10:10:17.372961',NULL);
INSERT INTO "fila_sincronizacao" VALUES(249,'POST','/produto','{"codigo_pdv": "T59602", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:00:02.052721','2026-10-01T10:10:20.619916',NULL);
INSERT INTO "fila_sincronizacao" VALUES(250,'DELETE','/produto/102','{}','ENVIADO',0,'2026-10-01T10:00:02.059430','2026-10-01T10:10:23.786529',NULL);
INSERT INTO "fila_sincronizacao" VALUES(251,'POST','/comandas/56/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T10:00:02.664402','2026-10-01T10:10:27.023845',NULL);
INSERT INTO "fila_sincronizacao" VALUES(252,'POST','/comandas/56/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-10-01T10:00:02.669491','2026-10-01T10:10:30.573504',NULL);
INSERT INTO "fila_sincronizacao" VALUES(254,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:00:03.290070','2026-10-01T10:10:49.805351',NULL);
INSERT INTO "fila_sincronizacao" VALUES(255,'DELETE','/produto/103','{}','ENVIADO',0,'2026-10-01T10:00:03.296140','2026-10-01T10:10:52.970472',NULL);
INSERT INTO "fila_sincronizacao" VALUES(257,'POST','/produto','{"codigo_pdv": "T59603", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:00:03.919347','2026-10-01T10:11:12.300185',NULL);
INSERT INTO "fila_sincronizacao" VALUES(258,'PATCH','/produto/104','{"codigo_pdv": "T59603", "nome": "Ancho Especial Parrilla (Atualizado)", "categoria": "Carnes", "preco": 89.0, "descricao": "Descricao atualizada para teste.", "url_imagem": "https://images.unsplash.com/photo-atualizada", "qtd_disp": 5, "precisa_produzir": false, "disponivel": false}','ENVIADO',0,'2026-10-01T10:00:03.928948','2026-10-01T10:11:15.475875',NULL);
INSERT INTO "fila_sincronizacao" VALUES(259,'DELETE','/produto/104','{}','ENVIADO',0,'2026-10-01T10:00:03.937199','2026-10-01T10:11:18.674168',NULL);
INSERT INTO "fila_sincronizacao" VALUES(260,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:00:04.678444','2026-10-01T10:11:21.924739',NULL);
INSERT INTO "fila_sincronizacao" VALUES(261,'POST','/comandas/58/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-10-01T10:00:04.691384','2026-10-01T10:11:25.348528',NULL);
INSERT INTO "fila_sincronizacao" VALUES(263,'DELETE','/produto/105','{}','ENVIADO',0,'2026-10-01T10:00:04.708607','2026-10-01T10:11:44.318666',NULL);
INSERT INTO "fila_sincronizacao" VALUES(264,'POST','/comandas/59/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-10-01T10:00:04.716379','2026-10-01T10:11:47.547741',NULL);
INSERT INTO "fila_sincronizacao" VALUES(265,'POST','/comandas/59/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-10-01T10:00:04.718382','2026-10-01T10:11:50.862327',NULL);
INSERT INTO "fila_sincronizacao" VALUES(266,'POST','/produto','{"codigo_pdv": "T59723", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:02:03.431537','2026-10-01T10:11:54.333678',NULL);
INSERT INTO "fila_sincronizacao" VALUES(267,'DELETE','/produto/106','{}','ENVIADO',0,'2026-10-01T10:02:03.435405','2026-10-01T10:11:57.490475',NULL);
INSERT INTO "fila_sincronizacao" VALUES(268,'POST','/comandas/60/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T10:02:03.873997','2026-10-01T10:12:00.728399',NULL);
INSERT INTO "fila_sincronizacao" VALUES(269,'POST','/comandas/60/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-10-01T10:02:03.878938','2026-10-01T10:12:03.928435',NULL);
INSERT INTO "fila_sincronizacao" VALUES(271,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:02:04.382970','2026-10-01T10:12:23.458001',NULL);
INSERT INTO "fila_sincronizacao" VALUES(272,'DELETE','/produto/107','{}','ENVIADO',0,'2026-10-01T10:02:04.387150','2026-10-01T10:12:26.628319',NULL);
INSERT INTO "fila_sincronizacao" VALUES(274,'POST','/produto','{"codigo_pdv": "T59724", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:02:04.883098','2026-10-01T10:12:45.841775',NULL);
INSERT INTO "fila_sincronizacao" VALUES(275,'PATCH','/produto/108','{"codigo_pdv": "T59724", "nome": "Ancho Especial Parrilla (Atualizado)", "categoria": "Carnes", "preco": 89.0, "descricao": "Descricao atualizada para teste.", "url_imagem": "https://images.unsplash.com/photo-atualizada", "qtd_disp": 5, "precisa_produzir": false, "disponivel": false}','ENVIADO',0,'2026-10-01T10:02:04.891414','2026-10-01T10:12:49.018465',NULL);
INSERT INTO "fila_sincronizacao" VALUES(276,'DELETE','/produto/108','{}','ENVIADO',0,'2026-10-01T10:02:04.899259','2026-10-01T10:12:52.196159',NULL);
INSERT INTO "fila_sincronizacao" VALUES(277,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:02:05.472804','2026-10-01T10:12:55.658388',NULL);
INSERT INTO "fila_sincronizacao" VALUES(278,'POST','/comandas/62/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-10-01T10:02:05.487190','2026-10-01T10:12:58.961646',NULL);
INSERT INTO "fila_sincronizacao" VALUES(280,'DELETE','/produto/109','{}','ENVIADO',0,'2026-10-01T10:02:05.509435','2026-10-01T10:13:18.021627',NULL);
INSERT INTO "fila_sincronizacao" VALUES(281,'POST','/comandas/63/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-10-01T10:02:05.528425','2026-10-01T10:13:21.769799',NULL);
INSERT INTO "fila_sincronizacao" VALUES(282,'POST','/comandas/63/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-10-01T10:02:05.530183','2026-10-01T10:13:24.993272',NULL);
INSERT INTO "fila_sincronizacao" VALUES(283,'POST','/produto','{"codigo_pdv": "T61276", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:27:56.238579','2026-10-01T10:27:57.577132',NULL);
INSERT INTO "fila_sincronizacao" VALUES(284,'DELETE','/produto/110','{}','ENVIADO',0,'2026-10-01T10:27:56.252824','2026-10-01T10:28:00.814513',NULL);
INSERT INTO "fila_sincronizacao" VALUES(285,'POST','/comandas/64/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T10:27:56.791418','2026-10-01T10:28:05.155199',NULL);
INSERT INTO "fila_sincronizacao" VALUES(286,'POST','/comandas/64/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-10-01T10:27:56.810195','2026-10-01T10:28:08.340768',NULL);
INSERT INTO "fila_sincronizacao" VALUES(288,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:27:57.354922','2026-10-01T10:28:29.505495',NULL);
INSERT INTO "fila_sincronizacao" VALUES(289,'DELETE','/produto/111','{}','ENVIADO',0,'2026-10-01T10:27:57.367884','2026-10-01T10:28:32.672092',NULL);
INSERT INTO "fila_sincronizacao" VALUES(291,'POST','/produto','{"codigo_pdv": "T61277", "nome": "Ancho Especial Parrilla", "categoria": "Carnes", "preco": 84.5, "descricao": "Ojo de bife nobre com marmoreio intenso grelhado na brasa viva.", "url_imagem": "https://images.unsplash.com/photo-1558030006-450675393462?w=600", "qtd_disp": 14, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:27:57.922872','2026-10-01T10:28:52.142183',NULL);
INSERT INTO "fila_sincronizacao" VALUES(292,'PATCH','/produto/112','{"codigo_pdv": "T61277", "nome": "Ancho Especial Parrilla (Atualizado)", "categoria": "Carnes", "preco": 89.0, "descricao": "Descricao atualizada para teste.", "url_imagem": "https://images.unsplash.com/photo-atualizada", "qtd_disp": 5, "precisa_produzir": false, "disponivel": false}','ENVIADO',0,'2026-10-01T10:27:57.944131','2026-10-01T10:28:55.316215',NULL);
INSERT INTO "fila_sincronizacao" VALUES(293,'DELETE','/produto/112','{}','ENVIADO',0,'2026-10-01T10:27:57.966373','2026-10-01T10:28:58.491709',NULL);
INSERT INTO "fila_sincronizacao" VALUES(294,'POST','/produto','{"codigo_pdv": "TEST_ESTOQUE_01", "nome": "Prato Teste Estoque", "categoria": "Carnes", "preco": 50.0, "descricao": "Prato para teste de estoque", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 2, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:27:58.719076','2026-10-01T10:29:02.041698',NULL);
INSERT INTO "fila_sincronizacao" VALUES(295,'POST','/comandas/66/itens','{"produto_query": "Prato Teste Estoque", "quantidade": 2, "observacao": ""}','ENVIADO',0,'2026-10-01T10:27:58.752754','2026-10-01T10:29:05.658557',NULL);
INSERT INTO "fila_sincronizacao" VALUES(297,'DELETE','/produto/113','{}','ENVIADO',0,'2026-10-01T10:27:58.809642','2026-10-01T10:29:25.851570',NULL);
INSERT INTO "fila_sincronizacao" VALUES(298,'POST','/comandas/67/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": "Sem cebola"}','ENVIADO',0,'2026-10-01T10:27:58.842674','2026-10-01T10:29:29.145868',NULL);
INSERT INTO "fila_sincronizacao" VALUES(299,'POST','/comandas/67/itens','{"produto_query": "Suco de Maracujá", "quantidade": 2, "observacao": "Bem gelada"}','ENVIADO',0,'2026-10-01T10:27:58.849064','2026-10-01T10:29:32.463994',NULL);
INSERT INTO "fila_sincronizacao" VALUES(300,'POST','/produto','{"codigo_pdv": "T61437", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:30:37.583749','2026-10-01T10:30:38.670510',NULL);
INSERT INTO "fila_sincronizacao" VALUES(301,'DELETE','/produto/114','{}','ENVIADO',0,'2026-10-01T10:30:37.595084','2026-10-01T10:30:41.901096',NULL);
INSERT INTO "fila_sincronizacao" VALUES(302,'POST','/comandas/68/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T10:30:38.119501','2026-10-01T10:30:46.289092',NULL);
INSERT INTO "fila_sincronizacao" VALUES(303,'POST','/comandas/68/itens','{"produto_query": "Suco de Goiaba", "quantidade": 1, "observacao": ""}','ENVIADO',0,'2026-10-01T10:30:38.141574','2026-10-01T10:30:49.924965',NULL);
INSERT INTO "fila_sincronizacao" VALUES(305,'POST','/produto','{"codigo_pdv": "9997", "nome": "&lt;script&gt;alert(&#x27;hack&#x27;)&lt;/script&gt;", "categoria": "&lt;b&gt;Carnes&lt;/b&gt;", "preco": 25.0, "descricao": "", "url_imagem": "", "qtd_disp": 15, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:30:38.744243','2026-10-01T10:31:09.212882',NULL);
INSERT INTO "fila_sincronizacao" VALUES(317,'POST','/produto','{"codigo_pdv": "T62659", "nome": "Picanha Teste Smokehouse", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre com brasa forte.", "url_imagem": "https://images.unsplash.com/photo-1544025162-d76694265947", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T10:50:59.151650','2026-10-01T10:51:00.764920',NULL);
INSERT INTO "fila_sincronizacao" VALUES(319,'POST','/comandas/72/itens','{"produto_query": "Suco de Goiaba", "quantidade": 2, "observacao": "Sem pimenta"}','ENVIADO',0,'2026-10-01T10:50:59.640946','2026-10-01T10:51:07.143410',NULL);
INSERT INTO "fila_sincronizacao" VALUES(335,'PATCH','/produto/1','{"codigo_pdv": "1", "nome": "Tutu à Mineira", "categoria": "Comida", "preco": 45.0, "descricao": "Feijão refogado e engrossado com farinha de mandioca, servido com torresmo crocante, couve refogada, ovo frito e arroz branco.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 30, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T11:01:00.755184','2026-10-01T11:01:02.099340',NULL);
INSERT INTO "fila_sincronizacao" VALUES(336,'PATCH','/produto/1','{"codigo_pdv": "1", "nome": "Tutu à Mineira", "categoria": "Comida", "preco": 40.5, "descricao": "Feijão refogado e engrossado com farinha de mandioca, servido com torresmo crocante, couve refogada, ovo frito e arroz branco.", "url_imagem": "https://i.imgur.com/f8OmDlH.jpeg", "qtd_disp": 30, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T11:03:18.479900','2026-10-01T11:03:20.332999',NULL);
INSERT INTO "fila_sincronizacao" VALUES(339,'PATCH','/produto/11','{"codigo_pdv": "10", "nome": "Suco de Laranja Natural", "categoria": "Bebidas", "preco": 10.0, "descricao": "Suco fresco de laranjas selecionadas, adoçado ou natural.", "url_imagem": "https://i.imgur.com/VjorB1O.jpeg", "qtd_disp": 40, "precisa_produzir": false, "disponivel": true}','ENVIADO',0,'2026-10-01T11:04:57.220992','2026-10-01T11:04:58.472208',NULL);
INSERT INTO "fila_sincronizacao" VALUES(340,'PATCH','/produto/117','{"codigo_pdv": "15", "nome": "Picanha Smokehouse Parrilla", "categoria": "Carnes", "preco": 69.9, "descricao": "Corte nobre.", "url_imagem": "", "qtd_disp": 10, "precisa_produzir": true, "disponivel": true}','ENVIADO',0,'2026-10-01T11:12:34.896150','2026-10-01T11:12:36.782434',NULL);
INSERT INTO "fila_sincronizacao" VALUES(341,'PATCH','/produto/13','{"codigo_pdv": "12", "nome": "Suco de Goiaba", "categoria": "Carnes", "preco": 16.33, "descricao": "Suco cremoso de goiaba, feito com fruta fresca.", "url_imagem": "https://i.imgur.com/M3ge2PL.jpeg", "qtd_disp": 45, "precisa_produzir": false, "disponivel": true}','ENVIADO',0,'2026-10-01T11:15:51.929835','2026-10-01T11:15:53.751551',NULL);
INSERT INTO "fila_sincronizacao" VALUES(342,'POST','/colaborador','{"id": 2, "nome": "Operador Caixa Teste", "email": "caixa_teste_automated@churrascontrol.com", "numero": "(11) 98765-4321", "cargo": "caixa", "primeiro_acesso": 1}','PENDENTE',4,'2026-10-06T10:03:17.582140','2026-10-06T10:03:42.986999','HTTP 404: {"code":"ERROR_CODE_NOT_FOUND","message":"Unable to locate request."}');
INSERT INTO "fila_sincronizacao" VALUES(343,'POST','/colaborador','{"id": 3, "nome": "Colaborador Teste Troca", "email": "troca_senha_test@churrascontrol.com", "numero": "(11) 91111-2222", "cargo": "caixa", "primeiro_acesso": 1}','PENDENTE',0,'2026-10-06T10:03:17.587622',NULL,NULL);
INSERT INTO "fila_sincronizacao" VALUES(344,'PATCH','/colaborador/3','{"primeiro_acesso": 0, "atualizado_em": "2026-10-06T10:03:17.588839"}','PENDENTE',0,'2026-10-06T10:03:17.591095',NULL,NULL);
INSERT INTO "fila_sincronizacao" VALUES(345,'DELETE','/colaborador/3','{}','PENDENTE',0,'2026-10-06T10:03:17.595612',NULL,NULL);
INSERT INTO "fila_sincronizacao" VALUES(346,'POST','/colaborador','{"id": 4, "nome": "Usuário Descartável", "email": "deletar_test@churrascontrol.com", "numero": "(11) 94444-5555", "cargo": "caixa", "primeiro_acesso": 1}','PENDENTE',0,'2026-10-06T10:03:17.602272',NULL,NULL);
INSERT INTO "fila_sincronizacao" VALUES(347,'DELETE','/colaborador/4','{}','PENDENTE',0,'2026-10-06T10:03:17.605171',NULL,NULL);
CREATE TABLE itens_comanda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comanda_id INTEGER NOT NULL,
                produto_id INTEGER,
                nome_produto_historico TEXT NOT NULL,
                categoria_historico TEXT,
                quantidade INTEGER NOT NULL DEFAULT 1,
                preco_momento REAL NOT NULL,
                observacao TEXT DEFAULT '',
                FOREIGN KEY(comanda_id) REFERENCES comandas(id) ON DELETE CASCADE
            );
INSERT INTO "itens_comanda" VALUES(2,2,1,'Tutu à Mineira','Comida',6,32.23,'');
INSERT INTO "itens_comanda" VALUES(3,3,28,'picangha','Carnes',4,50.0,'');
INSERT INTO "itens_comanda" VALUES(4,3,5,'Tropeiro','Comida',5,34.0,'');
INSERT INTO "itens_comanda" VALUES(5,5,1,'Tutu à Mineira','Comida',2,32.23,'');
INSERT INTO "itens_comanda" VALUES(7,5,15,'Suco de Cupuaçu','Bebida',1,13.0,'');
INSERT INTO "itens_comanda" VALUES(8,8,1,'Tutu à Mineira','Comida',3,32.23,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(9,11,1,'Tutu à Mineira','Comida',3,32.23,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(10,13,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(11,15,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(12,17,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(13,19,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(14,21,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(16,23,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(17,23,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(19,25,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(20,25,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(21,26,13,'Suco de Goiaba','Bebida',5,12.0,'');
INSERT INTO "itens_comanda" VALUES(23,28,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(24,28,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(26,30,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(27,30,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(28,31,13,'Suco de Goiaba','Bebida',4,12.0,'');
INSERT INTO "itens_comanda" VALUES(30,33,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(31,33,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(33,35,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(34,35,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(37,38,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(38,38,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(39,39,13,'Suco de Goiaba','Bebida',2,12.0,'');
INSERT INTO "itens_comanda" VALUES(41,41,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(42,41,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(44,43,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(45,43,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(46,36,50,'Ancho Especial Parrilla','Carnes',1,84.5,'');
INSERT INTO "itens_comanda" VALUES(48,45,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(49,45,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(51,47,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(52,47,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(53,48,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(55,51,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(56,51,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(57,52,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(59,55,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(60,55,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(61,56,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(63,59,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(64,59,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(65,60,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(67,63,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(68,63,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(69,64,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(71,67,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(72,67,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(73,68,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(75,71,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(76,71,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(77,72,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(79,75,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(80,75,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(81,76,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(83,79,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(84,79,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(85,80,13,'Suco de Goiaba','Bebida',3,12.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(87,83,13,'Suco de Goiaba','Bebida',1,12.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(88,83,14,'Suco de Maracujá','Bebida',2,11.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(89,84,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(91,87,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(92,87,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(93,88,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(95,91,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(96,91,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(97,92,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(99,95,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(100,95,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(101,96,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(103,99,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(104,99,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(105,100,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(107,103,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(108,103,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(109,104,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(111,107,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(112,107,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(113,108,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(115,111,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(116,111,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(117,112,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(119,115,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(120,115,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(121,116,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(123,119,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(124,119,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(125,120,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(127,123,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(128,123,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(129,124,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(131,127,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(132,127,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
INSERT INTO "itens_comanda" VALUES(133,128,14,'Suco de Maracujá','Bebida',3,11.0,'Sem pimenta');
INSERT INTO "itens_comanda" VALUES(135,131,14,'Suco de Maracujá','Bebida',1,11.0,'Sem cebola');
INSERT INTO "itens_comanda" VALUES(136,131,15,'Suco de Cupuaçu','Bebida',2,13.0,'Bem gelada');
CREATE TABLE mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_mesa INTEGER UNIQUE NOT NULL,
                capacidade INTEGER DEFAULT 1,
                status TEXT DEFAULT 'OCUPADA'
            );
INSERT INTO "mesas" VALUES(35,1,4,'OCUPADA');
CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_pdv TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco_unitario REAL NOT NULL
            , descricao TEXT DEFAULT '', url_imagem TEXT DEFAULT '', qtd_disp INTEGER DEFAULT 15, precisa_produzir INTEGER DEFAULT 1, disponivel INTEGER DEFAULT 1);
INSERT INTO "produtos" VALUES(1,'1','Tutu à Mineira','Comida',40.5,'Feijão refogado e engrossado com farinha de mandioca, servido com torresmo crocante, couve refogada, ovo frito e arroz branco.','https://i.imgur.com/f8OmDlH.jpeg',30,1,1);
INSERT INTO "produtos" VALUES(2,'2','Frango com Quiabo','Comida',30.32,'Coxas e sobrecoxas de frango cozidas em molho caseiro, acompanhadas de quiabo refogado, angu cremoso e arroz soltinho.','https://i.imgur.com/FnpgHh4.jpeg',30,1,1);
INSERT INTO "produtos" VALUES(3,'3','Feijoada Mineira','Comida',45.0,'Feijoada completa com carnes suínas, linguiça, paio, costelinha, servida com couve, farofa, laranja e arroz branco.','https://i.imgur.com/LKstJgW.jpeg',30,1,1);
INSERT INTO "produtos" VALUES(4,'4','Vaca Atolada','Comida',38.0,'Costela bovina cozida lentamente com mandioca macia, temperada com ervas, acompanhada de arroz e cheiro-verde.','https://i.imgur.com/ggAIiWT.jpeg',30,1,1);
INSERT INTO "produtos" VALUES(5,'5','Tropeiro','Comida',34.0,'Feijão tropeiro com linguiça, bacon, torresmo, ovo, farofa e couve crocante, servido com arroz branco.','https://i.imgur.com/w1Ztl50.jpeg',30,1,1);
INSERT INTO "produtos" VALUES(6,'6','Bambá de Couve','Comida',28.0,'Mingau de milho cremoso com couve refogada e linguiça frita, acompanhado de torresmo e arroz.','https://i.imgur.com/TqZrOp8.jpeg',20,1,0);
INSERT INTO "produtos" VALUES(7,'7','Lombo com Canjiquinha','Comida',36.0,'Lombo suíno assado, servido com canjiquinha temperada e couve à mineira.','https://i.imgur.com/EHR7JvI.jpeg',10,1,0);
INSERT INTO "produtos" VALUES(8,'8','Carne de Panela','Comida',35.0,'Carne bovina cozida em molho rústico com batatas, acompanhada de arroz, feijão e macarrão caseiro.','https://i.imgur.com/WLnQx5P.jpeg',40,1,1);
INSERT INTO "produtos" VALUES(10,'9','Costelinha com Ora-pro-nóbis','Promoção',40.0,'Costelinha suína frita, acompanhada de ora-pro-nóbis refogada, angu e arroz branco.','https://i.imgur.com/djE61fW.jpeg',30,1,1);
INSERT INTO "produtos" VALUES(11,'10','Suco de Laranja Natural','Bebidas',10.0,'Suco fresco de laranjas selecionadas, adoçado ou natural.','https://i.imgur.com/VjorB1O.jpeg',50,0,1);
INSERT INTO "produtos" VALUES(12,'11','Suco de Caju','Promoção',10.0,'Suco refrescante de caju, preparado com polpa natural.','https://i.imgur.com/p26Fved.jpeg',20,0,1);
INSERT INTO "produtos" VALUES(13,'12','Suco de Goiaba','Carnes',16.33,'Suco cremoso de goiaba, feito com fruta fresca.','https://i.imgur.com/M3ge2PL.jpeg',30,0,1);
INSERT INTO "produtos" VALUES(14,'13','Suco de Maracujá','Bebida',11.0,'Suco de maracujá natural, com toque azedinho e refrescante','https://i.imgur.com/s6AvzxI.jpeg',12,0,1);
INSERT INTO "produtos" VALUES(15,'14','Suco de Cupuaçu','Bebida',13.0,'Suco exótico de cupuaçu, típico do interior mineiro.','https://i.imgur.com/04zADDs.jpeg',26,0,1);
INSERT INTO "produtos" VALUES(117,'15','Picanha Smokehouse Parrilla','Carnes',69.9,'Picanha maturada na parrilla com chimichurri artesanal.','https://i.imgur.com/VjorB1O.jpeg',25,1,1);
CREATE TABLE qrcodes_mesas (
                numero_mesa INTEGER PRIMARY KEY,
                token_qrcode TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );
INSERT INTO "qrcodes_mesas" VALUES(1,'m1-5c0d6c1a','2026-09-30T14:05:05.268478','2026-10-06T10:03:41.537699');
INSERT INTO "qrcodes_mesas" VALUES(2,'m2-c84a2976','2026-09-30T14:05:05.268533','2026-09-30T14:11:35.135686');
INSERT INTO "qrcodes_mesas" VALUES(3,'mesa-3-token','2026-09-30T14:05:05.268539','2026-09-30T14:05:05.268539');
INSERT INTO "qrcodes_mesas" VALUES(4,'mesa-4-token','2026-09-30T14:05:05.268543','2026-09-30T14:05:05.268543');
INSERT INTO "qrcodes_mesas" VALUES(5,'mesa-5-token','2026-09-30T14:05:05.268546','2026-09-30T14:05:05.268546');
INSERT INTO "qrcodes_mesas" VALUES(6,'mesa-6-token','2026-09-30T14:05:05.268549','2026-09-30T14:05:05.268549');
INSERT INTO "qrcodes_mesas" VALUES(7,'mesa-7-token','2026-09-30T14:05:05.268553','2026-09-30T14:05:05.268553');
INSERT INTO "qrcodes_mesas" VALUES(8,'mesa-8-token','2026-09-30T14:05:05.268556','2026-09-30T14:05:05.268556');
INSERT INTO "qrcodes_mesas" VALUES(9,'mesa-9-token','2026-09-30T14:05:05.268559','2026-09-30T14:05:05.268559');
INSERT INTO "qrcodes_mesas" VALUES(10,'mesa-10-token','2026-09-30T14:05:05.268562','2026-09-30T14:05:05.268562');
CREATE UNIQUE INDEX idx_comanda_unica_aberta 
            ON comandas(mesa_id) WHERE status = 'ABERTA';
CREATE INDEX idx_produtos_codigo ON produtos(codigo_pdv);
CREATE INDEX idx_itens_comanda_cid ON itens_comanda(comanda_id);
CREATE INDEX idx_comandas_status ON comandas(status);
CREATE INDEX idx_fila_status ON fila_sincronizacao(status);
CREATE INDEX idx_produtos_categoria ON produtos(categoria);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('produtos',179);
INSERT INTO "sqlite_sequence" VALUES('mesas',130);
INSERT INTO "sqlite_sequence" VALUES('comandas',131);
INSERT INTO "sqlite_sequence" VALUES('itens_comanda',136);
INSERT INTO "sqlite_sequence" VALUES('fila_sincronizacao',347);
INSERT INTO "sqlite_sequence" VALUES('colaboradores',7);
COMMIT;
