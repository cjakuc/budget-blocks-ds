# Budget Blocks DS API

## Contributers

| Adriann Lefebvere | Christopher Jakuc |
|:--:|:--:|
| <img src="https://media-exp1.licdn.com/dms/image/C5603AQHnWP2pLXNElA/profile-displayphoto-shrink_200_200/0?e=1597881600&v=beta&t=4mkgFZn0Ny3TO2vC6IA0atRSJNjrhA1OstP0kSkDdtc" width=200> | <img src="https://media-exp1.licdn.com/dms/image/C5603AQF1rn6d_fEWRQ/profile-displayphoto-shrink_200_200/0?e=1597881600&v=beta&t=5_hQV3iFj87RiQZzLMr76c7G63yL8O4PI29KeBsgbqw" width=200> |
|:--:|:--:|

## Local Setup
* Clone this repo and cd into the directory
* `pipenv install` to create the pip enviroment
* `pipenv shell` to enter the pip enviroment
* Type `uvicorn main:app --reload` to run the server locally

## API Framework and Deployment
The data science api was created with fastAPI and was deployed to AWS Elastic Beanstalk

## API Documentation
The API documentation can be found in the deployed version of the api [here](https://api.budgetblocks.org/docs)
