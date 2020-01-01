from gutenberg.acquire import get_metadata_cache

if __name__ == '__main__':
    cache = get_metadata_cache()
    cache.populate()
