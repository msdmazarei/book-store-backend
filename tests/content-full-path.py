from books.controllers.content_path_finder import return_content_full_path

if __name__ == '__main__':
    content={
  "BookType": 2,
  "PackagingVersion": 0,
  "title": "کتاب صوتی تستی نمونه اول",
  "children": [
    {
      "title": "فصل اول",
      "body": [
        {
          "type": "voice",
          "voice":"retyuioplkjhgfvbnm"
        }

      ],
      "children": [
      ]
    }]
    }
    return_content_full_path(content)