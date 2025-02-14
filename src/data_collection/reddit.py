import os, json, uuid
from tqdm import tqdm
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from src.models.zreader import Zreader
from src.models.schemas.post import Post
from src.models.schemas.comment import Comment
from src.db import engine


def generate_new_id(original_id: str) -> str:
    return f"{original_id}_{uuid.uuid4().hex[:8]}"


def create_post_instance(record: dict) -> Post:
    """
    convert a record (dict) into a Post
    """
    record["subreddit"] = record.get("subreddit", "").lower()
    return Post(**record)


def create_comment_instance(record: dict) -> Comment:
    """
    convert a record (dict) into a Comment, if 'link_id' starts with 't3_', strip that prefix to get post_id
    """
    record["subreddit"] = record.get("subreddit", "").lower()

    link_id = record.get("link_id")
    if isinstance(link_id, str) and link_id.startswith("t3_"):
        post_id = link_id[3:]
        record["post_id"] = post_id

    return Comment(**record)


def process_batch(session: Session, items: list, model_class) -> None:
    """
    insert Post or Comment into db, handling duplicate conflicts
    """
    for item in items:
        original_id = item.id
        retry_count = 0

        while retry_count < 3:
            try:
                session.add(item)
                session.flush()  # Detect conflicts before final commit
                break  # success
            except IntegrityError:
                session.rollback()
                item.id = generate_new_id(original_id)
                retry_count += 1
            except Exception as e:
                print(f"Error processing {model_class.__name__} {item.id}: {e}")
                session.rollback()
                break

        if retry_count == 3:
            print(
                f"Failed after 3 retries for {model_class.__name__} with ID: {original_id}"
            )

    try:
        session.commit()
    except Exception as e:
        print("Error committing batch:", e)
        session.rollback()


def read_zstd_reddit_data(
    file_path: str,
    create_func,
    model_class,
    desc: str = "Reading data",
    batch_size: int = 10000,
) -> None:
    """
    read a .zst file, parse JSON into a model, and batch-insert to DB. skip lines missing 'id' or invalid JSON
    """
    with Session(engine) as session:
        zreader = Zreader(file_path)
        items_cache = []
        malformed_count = 0

        for line in tqdm(zreader.readlines(), desc=desc, leave=False):
            try:
                data = json.loads(line)
                if not isinstance(data, dict) or "id" not in data:
                    malformed_count += 1
                    continue

                item = create_func(data)
                items_cache.append(item)

                if len(items_cache) >= batch_size:
                    process_batch(session, items_cache, model_class)
                    items_cache.clear()
            except json.JSONDecodeError:
                malformed_count += 1

        # leftover items
        if items_cache:
            process_batch(session, items_cache, model_class)

        zreader.close()
        print(f"Malformed lines: {malformed_count}")


def read_posts(file_path: str) -> None:
    """
    Ingest a .zst file containing Reddit posts into the database.
    """
    read_zstd_reddit_data(
        file_path=file_path,
        create_func=create_post_instance,
        model_class=Post,
        desc="Reading Posts",
    )


def read_comments(file_path: str) -> None:
    """
    Ingest a .zst file containing Reddit comments into the database.
    Extracts post_id from link_id (prefix 't3_').
    """
    read_zstd_reddit_data(
        file_path=file_path,
        create_func=create_comment_instance,
        model_class=Comment,
        desc="Reading Comments",
    )


def process_zst_files_in_directory(data_folder: str) -> None:
    for filename in os.listdir(data_folder):
        file_path = os.path.join(data_folder, filename)
        if "submissions" in filename:
            print(f"Processing submissions file: {filename}")
            read_posts(file_path)
        elif "comments" in filename:
            print(f"Processing comments file: {filename}")
            read_comments(file_path)
        else:
            print(f"Skipping unknown file: {filename}")


def inspect_zst_file_headers(file_path: str, num_lines: int = 5) -> None:
    zreader = Zreader(file_path)
    print(f"First {num_lines} lines of {file_path}:")
    for i, line in enumerate(zreader.readlines()):
        if i >= num_lines:
            break
        try:
            data = json.loads(line)
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print(f"Malformed line: {line}")
    zreader.close()


if __name__ == "__main__":
    # file_path = "data/raw/reddit/Bitcoin_comments.zst"
    # inspect_zst_file_headers(file_path, num_lines=3)

    data_folder = "data/raw/reddit"
    process_zst_files_in_directory(data_folder)
