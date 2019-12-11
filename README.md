JEWELLERY RECOMMENDATION

1\. PROBLEM STATEMENT

With a wide array of unique products available for offer,
recommendations prove to be a difficult problem to solve for any
retailer. Additionally, recommendations based solely off images prove to
be even more difficult due to the structure of the data. So, given the
problem of designing the backend for a chatbot capable of recommendation
by image inputs, the selected method must be able to both process and
infer from large quantities of image data.

Neural networks are ideal for these types of problems as they are able
to process large quantities of data, infer complex, non-linear
relationships between quantitative and spatial data, and are able to
better model heteroskedasticity compared to more traditional machine
learning techniques.

2\. DATA

The data set used in the training of this model consisted of 7 594
images of jewellery with 988 anklets, 1 162 bracelets, 906 charms, 1 137
earrings, 1 114 necklaces, 1 283 rings, and 1 007 single rings. The
images were sourced from public-domain images posted on Etsy, Instagram,
and Pinterest and manually checked to verify the classification label.
Reflections along the horizontal and vertical axes, rotations up to
360°, zoom up to 1.5x, and minimum lighting up to 40% of stock were
applied to the training images to allow for the identification of a
greater range of images.

The data for the recommender was sourced from scraped information off
the Meijuri site. Only the main image (the piece of jewellery on a white
background) was used to compute the similarity with the feature vectors
of the provided image derived from the model.


3\. MODELLING

A convolutional neural network (CNN) was used to classify the images to
the seven classes of jewellery. The hooked output of the final feature
layer of the neural network (consisting of 512 features) was extracted
to compute feature similarity among images. Cosine similarity was used
to compute this similarity as the recommended results appeared to be the
most logically similar by eye compared to the results produced using
Euclidean distance. The error in the classification process resulted in
an accuracy of \~82% in the validation.


4\. RESULTS

Images recommended by the model appear to be very similar to the
provided image in a variety of factors including class, metal, colour,
and shape where similarities exist between the provided image and the
offerings from Meijuri. Since the model has relatively low accuracy and
no filtering exists, the recommender will not consistently recommend
like-items of jewellery (ex. if a ring is provided, the recommender will
only check for similar features accross all classes, not only provide
rings).

For better recommendations, a filtering method to specify exactly what
aspect of the image is desired to be compared would be ideal. This would
involve specifically extracting features using more traditional machine
learning techniques. So, a merging of the results of the neural network
recommendation and filtering using feature extraction would produce a
better recommendation model, this could be done in future works.
