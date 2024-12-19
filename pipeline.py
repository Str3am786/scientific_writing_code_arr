from extraction_amenity import pipeline as extraction_pipeline

def pipeline(review_text: str) -> list:

    if not (possible_amenities := extraction_pipeline(review_text)):
        return []

    available_amenities = []

    for amenity, contexts in possible_amenities.items():
        for context in contexts:
            #Send to model
            positive = True
            if positive:
                # The given amenity is positive
                break

        available_amenities.append(amenity)

    return available_amenities