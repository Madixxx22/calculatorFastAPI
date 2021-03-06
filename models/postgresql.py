from typing import Union

import asyncpg
from asyncpg.connection import Connection
from asyncpg.pool import Pool

from core.config import load_config

class Database:


    def __init__(self):
        self.pool: Union[Pool, None] =  None

    #Создаем подключение к БД postgresql
    async def create(self):
        config = load_config(".env")
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database,
        )

    #Обработчик Sql запросов, отправляющий по подключению данные или берущий из БД
    async def execute (self, command, *args,
                       fetch: bool = False,
                       fetchval: bool = False,
                       fetchrow: bool = False,
                       execute: bool = False
                       ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    #Создаем если нет таблицу с которой работает приложение
    async def create_table_users(self):
        sql="""
                CREATE TABLE IF NOT EXISTS calc_history(
                id_number SERIAL PRIMARY KEY,
                expression TEXT NOT NULL,
                result FLOAT NOT NULL,
                status VARCHAR(7) NOT NULL
                );
            """
        await self.execute(sql, execute=True)
    
    #Добавляет выполненные выражения в БД
    async def create_expression(self, expression, result, status):
        sql="""
                INSERT INTO calc_history(expression, result, status) VALUES ($1, $2, $3)
        """
        await self.execute(sql, expression, result, status, execute = True)

    #Производим выборку выражений их результата и статуса, и устанавливаем лимит получаемых данных
    async def expression_success(self, limit):
        sql = f"SELECT calc_history.expression, calc_history.result, status FROM calc_history ORDER BY id_number DESC LIMIT {limit}"
                
        return await self.execute(sql, fetch = True)