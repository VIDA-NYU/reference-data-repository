# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.


def test_load_cities(store):
    """Test downloading and loading the U.S. cities test dataset via the local
    data store.
    """
    df = store.load(key='cities', auto_download=True)
    assert df.shape == (7, 2)
    assert list(df.columns) == ['city', 'state']
    df = store.load(key='cities', columns=['city'])
    assert df.shape == (7, 1)
    assert list(df.columns) == ['city']
