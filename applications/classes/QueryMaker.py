class QueryMaker:

    def __init__(self):
        self.query = "select attributes from table"

    def add_select(self, attributes: str):
        self.query = self.query.replace('attributes', attributes)
        return self

    def add_table(self, table: str):
        self.query = self.query.replace('table', table)
        return self

    def add_where(self, condition: str):
        self.query += f' where {condition} '
        return self

    def add_group_by(self, condition: str):
        self.query += f' group by {condition} '
        return self

    def add_having(self, condition: str):
        self.query += f' having {condition}'
        return self
