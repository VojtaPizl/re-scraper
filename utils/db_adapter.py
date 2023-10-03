from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session

class DBAdapter:
    CONNECTION_STRING_TEMPLATE = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, database_name: str, user: str, password: str, host: str = 'localhost',
                 port: int = 5432, schema_name: str = 'public'):
        connection_string = self.CONNECTION_STRING_TEMPLATE.format(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database_name
        )
        self._schema = schema_name
        self._engine = create_engine(connection_string)
        self._session_cls = sessionmaker(bind=self._engine)

    @property
    def engine(self):
        """SQLAlchemy engine"""
        return self._engine

    def get_metadata(self) -> MetaData:
        """Get SQLAlchemy metadata"""
        return MetaData(schema=self._schema)

    def get_session(self, **kwargs) -> Session:
        """Create and return new session instance"""
        return self._session_cls(**kwargs)

    def clean(self) -> None:
        """Close all database connections"""
        self._engine.dispose()
        