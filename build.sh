# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

if [[ $CREATE_SUPERUSER ]];
then
  python shop/manage.py createsuperuser --no-input
fi