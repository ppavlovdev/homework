# Homework

### Local installation
```shell
$ python -m pip install poetry
$ poetry install
```

### Docker installation
```shell
$ docker compose up -d
```

### Routes
**Images**:
- [GET] /api/images
- [GET] /api/images/{id}
- [POST] /api/images
- [DELETE] /api/images/{id}
- [GET] /api/images/{id}/annotations
- [POST] /api/images/{id}/annotations

**Annotations**:
- [GET] /api/annotations/{id}
- [PUT] /api/annotations/{id}

## Problems and solutions
1. **How to upload image with annotations?**
    - Form-data with image and json string of annotations:
      - ❌ Declined due to the fact that we break the RESTful API semantics.
    - JSON with base64 encoded image and annotations:
      - ❌ Declined because base64 encoding increases the size of the data by ~33%. This solution suitable only for small images like thumbnails.
    - Separate requests for image and annotations:
      - ✅ Accepted. We don't break the RESTful API semantics and don't increase the size of the data.
<br><br>
2. **How to emulate tree structure in relational database?**
    - Adjacency list:
      - ❌ Declined due to recursive read quieries overhead.
    - Nested sets:
      - ❌ Declined due to slow write quieries.
    - Materialized path:
      - ✅ Accepted. Best speed for both read and write quieries with B-Tree index and `LIKE` queries with `%xxxx`-like predicate.
<br><br>
3. **How to store semi-structured data (annotations) in relational database?**
    - JSONB field:
      - ❌ Declined due to storage overhead and slow quieries (GIN index slows both for read and write operations).
    - Separate table for each annotation type:
      - ❌ Declined due to the fact that we don't know the number of annotation types in advance.
    - Flat table with type column:
        - ✅ Accepted. We don't break the relational database semantics and don't increase the size of the data. The only drawback is that we need to implement complex serialization/deserialization logic.

## Things I would do if I had more time
- [ ] Add tests
- [ ] Add authentication
- [ ] Add OpenAPI documentation
- [ ] Add nginx reverse proxy for image serving