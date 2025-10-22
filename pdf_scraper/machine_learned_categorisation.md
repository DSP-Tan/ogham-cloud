In the current implementation, we are finding the patterns which identify categories ourselves.
To find a title we apply the constraint that it is at the top of a page, that the text is larger
than the median font size of the page, etc.

Instead of finding these patterns ourselves, we could get a machine learning model, (a decision tree
for starters) to find them for us.

In order to do this we would first need a good batch of labelled documents. Then we would apply the
model to them, and we could inspect the model to see which patterns are used to make the decisions.

## Labelling the documents manually

To facilitate the manual labelling of models, we should write a script, or use a note book, which
will cycle through all the pages of the pdf. It will then allow the user to say whether or not a 
certain category is present, and if it is, to specify the lines that are a part of it.

So far, we have found rules for titles, subtitles, subsubtitles, and various other categories. What
we do not have so many rules for are outside of image captions.

dfs = []
for year in years:
    doc    = open_exam(year)
    images = get_images(doc)
    images = preproc_images(images)
    df     = parse_exam()     # This will apply all the successful categorisations already developed.
    for page in doc:
        if image in page:
            show_page()
            - ask user if there are captions
            if yes:
                - input captions until double carriage return
            else:
                continue
    dfs.append(df)
big_df = pd.concat(dfs)

## Enrich labelled df

We should add any information which may be useful to the model in identifying captions. What 
we are mostly lacking is the characteristics of a line relative to the rest of the document.
How much larger is the font of this text to the median text font size? Is it bold? Is it italic?
How far from the nearest image is it? How far from the nearest text is it? How much closer is the
cluster of which it is an element to the nearest image than it is to the nearest text cluster?


