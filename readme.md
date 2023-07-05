# Easy Share

## Installation

Optional
`bash
conda create -n dj python=3.10
conda activate dj
`

Requirements install
`bash
pip install -r requirements.txt
`

`bash
python manage.py makemigrations access sharefiles
`

`bash
python manage.py migirate
`

`bash
python manage.py collectstatic
`

`bash
python manage.py runserver
`

## TODO

- [ ] Large file chunked upload
- [ ] Api auth
- [ ] Api test by file
- [ ] User System
- [ ] Multiple working envs
- [ ] Nginx Deploy
