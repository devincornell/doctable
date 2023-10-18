---
title: "Introduction to doctable"
---

# Managing Connections

    core = newtable.ConnectCore.open(
        target=':memory:', 
        dialect='sqlite'
    )

Result:

    ConnectCore(target=':memory:', dialect='sqlite', engine=Engine(sqlite:///:memory:), metadata=MetaData())


@newtable.table_schema
class MyContainer0:
    id: int
    name: str
    age: int



with core.tablemaker() as tmaker:
    tab0 = tmaker.new_table(container_type=MyContainer0)


pprint.pprint(core.inspect_columns())



# Defining Schemas


## Table-level Parameters


## Column-level Parameters





