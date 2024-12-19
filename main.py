from pipeline import pipeline


if __name__ == "__main__":
    reviews = ["There is a kid", "There is a dog", "The play ground is broken"]
    all_amenities = []
    for review in reviews:
        all_amenities.extend(pipeline(review))

    text = "There is a cafe, there is a kid, the playground is broken"
    print(pipeline(text))