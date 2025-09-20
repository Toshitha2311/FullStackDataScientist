import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# -------------------- Setup --------------------
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb: Client = create_client(url, key)

# -------------------- Functions --------------------
def add_member(member_id, name, email):
    payload = {
        "member_id": member_id,
        "name": name,
        "email": email,
        "join_date": datetime.now().date().isoformat()
    }
    resp = sb.table("members").insert(payload).execute()
    return resp.data

def add_book(book_id, title, author, category, stock):
    payload = {
        "book_id": book_id,
        "title": title,
        "author": author,
        "category": category,
        "stock": stock
    }
    resp = sb.table("books").insert(payload).execute()
    return resp.data

def list_books():
    resp = sb.table("books").select("*").execute()
    books = resp.data or []
    print("\n📚 Books:")
    for b in books:
        print(f"- {b['title']} by {b['author']} | Category: {b['category']} | Stock: {b['stock']}")

def search_books(field, keyword):
    if field not in ["title", "author", "category"]:
        print("⚠️ Invalid search field")
        return
    resp = sb.table("books").select("*").ilike(field, f"%{keyword}%").execute()
    books = resp.data or []
    for b in books:
        print(f"- {b['title']} by {b['author']} | Category: {b['category']} | Stock: {b['stock']}")

def member_details(member_id):
    m_resp = sb.table("members").select("*").eq("member_id", member_id).execute()
    member = m_resp.data[0] if m_resp.data else None
    if not member:
        print(f"⚠️ Member ID {member_id} not found")
        return
    print(f"\n👤 {member['name']} | Email: {member['email']} | Joined: {member['join_date']}")
    br_resp = sb.table("borrow_records").select("book_id, borrow_date, return_date").eq("member_id", member_id).execute()
    records = br_resp.data or []
    if not records:
        print("No borrowed books.")
        return
    book_ids = [r["book_id"] for r in records]
    books_resp = sb.table("books").select("book_id, title").in_("book_id", book_ids).execute()
    book_map = {b["book_id"]: b["title"] for b in books_resp.data or []}
    print("Borrowed Books:")
    for r in records:
        title = book_map.get(r["book_id"], "Unknown")
        status = r.get("return_date") or "Not returned"
        print(f"- {title} | Borrowed on: {r['borrow_date']} | Return: {status}")

def update_member_email(member_id, new_email):
    sb.table("members").update({"email": new_email}).eq("member_id", member_id).execute()
    print(f"✅ Email updated for Member ID {member_id}")

def update_book_stock(book_id, new_stock):
    sb.table("books").update({"stock": new_stock}).eq("book_id", book_id).execute()
    print(f"✅ Stock updated for Book ID {book_id}")

def delete_member(member_id):
    borrowed = sb.table("borrow_records").select("*").eq("member_id", member_id).execute().data or []
    if borrowed:
        print("⚠️ Cannot delete member: Books not returned")
        return
    sb.table("members").delete().eq("member_id", member_id).execute()
    print("✅ Member deleted")

def delete_book(book_id):
    borrowed = sb.table("borrow_records").select("*").eq("book_id", book_id).execute().data or []
    if borrowed:
        print("⚠️ Cannot delete book: Currently borrowed")
        return
    sb.table("books").delete().eq("book_id", book_id).execute()
    print("✅ Book deleted")

def borrow_book(record_id, member_id, book_id):
    book_resp = sb.table("books").select("stock").eq("book_id", book_id).execute()
    stock = book_resp.data[0]["stock"] if book_resp.data else 0
    if stock < 1:
        print("⚠️ Book not available")
        return
    sb.table("books").update({"stock": stock - 1}).eq("book_id", book_id).execute()
    sb.table("borrow_records").insert({
        "record_id": record_id,
        "member_id": member_id,
        "book_id": book_id,
        "borrow_date": datetime.now().date().isoformat()
    }).execute()
    print("✅ Book borrowed successfully")

def return_book(record_id):
    br_resp = sb.table("borrow_records").select("book_id").eq("record_id", record_id).execute()
    if not br_resp.data:
        print("⚠️ Borrow record not found")
        return
    book_id = br_resp.data[0]["book_id"]
    sb.table("borrow_records").update({"return_date": datetime.now().date().isoformat()}).eq("record_id", record_id).execute()
    book_resp = sb.table("books").select("stock").eq("book_id", book_id).execute()
    stock = book_resp.data[0]["stock"] if book_resp.data else 0
    sb.table("books").update({"stock": stock + 1}).eq("book_id", book_id).execute()
    print("✅ Book returned successfully")

# -------------------- Main Menu --------------------
def main():
    while True:
        print("\n===== Library Management Menu =====")
        print("1. Add Member")
        print("2. Add Book")
        print("3. Update Member Email")
        print("4. Update Book Stock")
        print("5. Delete Member")
        print("6. Delete Book")
        print("7. Borrow Book")
        print("8. Return Book")
        print("9. List Books")
        print("10. Search Books")
        print("11. Member Details")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            member_id = int(input("Member ID: "))
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            add_member(member_id, name, email)
        elif choice == "2":
            book_id = int(input("Book ID: "))
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            category = input("Category: ").strip()
            stock = int(input("Stock: "))
            add_book(book_id, title, author, category, stock)
        elif choice == "3":
            member_id = int(input("Member ID: "))
            new_email = input("New Email: ").strip()
            update_member_email(member_id, new_email)
        elif choice == "4":
            book_id = int(input("Book ID: "))
            new_stock = int(input("New Stock: "))
            update_book_stock(book_id, new_stock)
        elif choice == "5":
            member_id = int(input("Member ID: "))
            delete_member(member_id)
        elif choice == "6":
            book_id = int(input("Book ID: "))
            delete_book(book_id)
        elif choice == "7":
            record_id = int(input("Record ID: "))
            member_id = int(input("Member ID: "))
            book_id = int(input("Book ID: "))
            borrow_book(record_id, member_id, book_id)
        elif choice == "8":
            record_id = int(input("Record ID: "))
            return_book(record_id)
        elif choice == "9":
            list_books()
        elif choice == "10":
            field = input("Search by (title/author/category): ").strip().lower()
            keyword = input("Keyword: ").strip()
            search_books(field, keyword)
        elif choice == "11":
            member_id = int(input("Member ID: "))
            member_details(member_id)
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("⚠️ Invalid choice, try again.")

if __name__ == "__main__":
    main()
