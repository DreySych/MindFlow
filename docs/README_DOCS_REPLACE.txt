Как заменить старую Sphinx-документацию
=======================================

1. Удали старую папку docs в проекте.
2. Скопируй эту папку docs на её место.
3. Из корня проекта запусти:

   pip install sphinx
   sphinx-build -b html docs/source docs/build/html

   или:

   cd docs
   make html

4. Открой файл:

   docs/build/html/index.html

5. Если используете GitLab CI, добавьте в .gitlab-ci.yml этап docs:

   docs:
     image: python:3.12
     script:
       - pip install -r requirements.txt
       - pip install sphinx
       - sphinx-build -b html docs/source docs/build/html
     artifacts:
       paths:
         - docs/build/html
