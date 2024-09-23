# Auction 🔨
> Student project 

This is a custom Auction service that provides you to create lots, make comments and set bids

You can see deployed project by the link below
> https://auction-7arl.onrender.com/

Use this credentials to log in:

**Username:** `test`

**Password:** `Pass12__`
## Getting started

1. Clone repository  
```shell
git clone https://github.com/dimak20/auction.git
cd auction
```
2. Then, create and activate .venv environment  
```shell
python -m venv env
```
For Unix system
```shell
source venv/bin/activate
```

For Windows system

```shell
venv\Scripts\activate
```

3. Install requirments.txt by the command below  


```shell
pip install -r requirements.txt
```

4. You need to make migrations
```shell
python manage.py makemigrations
python manage.py migrate
```
5. (Optional) Also you can load fixture data
```shell
python manage.py loaddata auction_data.json
```


6. And finally, create superuser and run server

```shell
python manage.py createsuperuser
python manage.py runserver # http://127.0.0.1:8000/
```


### Project configuration

Your project needs to have this structure


```plaintext
Project
├── Auction
│   ├── __init__.py
│   ├── models.py
│   └── views.py
│   ├──celery.py
│   ├── settings.py
│   └── urls.py
│
├── manage.py
│   
├── media
│   
├── static
│
├── tendering
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
└   ├── forms.py
│   ├── models.py
└   ├── tasks.py
│   ├── urls.py
│   └── views.py
└── requirements.txt
```


## Features

* Creation users
* Creation lots with set price and uploading photo
* Makin comments and bids under the lot detail
* Customising your profile by photo, bio and other information
* Tracking statistics on the home page

![Website Interface](Project.jpg)