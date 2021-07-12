FROM python:3.9-slim
WORKDIR /project
ADD . .
RUN pip install -r requirements_tests.txt
RUN pip install -r requirements.txt
CMD ["functions-framework", "--target", "app", "--debug"]