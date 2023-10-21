



import pandas as pd
import json

database = []
try:
    imported = pd.read_csv('./desidime/desidime_data.csv')
    for i in imported.values:
        title = i[1]
        website_name = i[2]
        product_link = i[3]
        view_count = i[4]
        hotness = i[5]
        original_price = i[6]
        deal_price = i[7]
        deal_percent = i[8]
        start_date = i[9]
        end_date = i[10]
        hot = i[11]
        active = i[12]
        groups = i[13]
        product_image = i[14]
        original_link = i[15]
        featured = i[16]
        description = i[17]
        obj = {
                    'link': original_link,
                    'title': title,
                    'website_name': website_name,
                    'product_link': product_link,
                    'view_count': view_count,
                    'hotness': hotness,
                    'original_price': original_price,
                    'deal_price': deal_price,
                    'discount_percentage': deal_percent,
                    'start_date': start_date,
                    'end_date': end_date,
                    'hot': hot,
                    'active': active,
                    'groups': groups,
                    'image': product_image,
                    'featured': featured,
                    'description': description
                }
        database.append(obj)
except:
    print('failed to read database')

scraped_data = []
for i in database:
    title = i['title']
    website_name = i['website_name']
    product_link = i['product_link']
    view_count = i['view_count']
    hotness = i['hotness']
    original_price = i['original_price']
    deal_price = i['deal_price']
    discount_percentage = i['discount_percentage']
    start_date = i['start_date']
    end_date = i['end_date']
    end_date = i['end_date']
    hot = i['hot']
    active = i['active']
    groups = i['groups']
    image = i['image']
    link = i['link']
    featured = i['featured']
    description = i['description']
    scraped_data.append([title,
        website_name, 
        product_link, 
        view_count, 
        hotness, 
        original_price, 
        deal_price, 
        discount_percentage, 
        start_date, 
        end_date, 
        hot, 
        active, 
        groups, 
        image, 
        link, 
        featured, 
        description])

headers = ['title', 'website_name', 'product_link', 'view_count', 'hotness', 'original_price', 'deal_price', 'discount_percentage', 'start_date', 'end_date', 'hot', 'active', 'groups', 'image', 'link', 'featured', 'description']
df = pd.DataFrame(columns = headers)

# Adding to the dataframe and exporting
for row in scraped_data:
    length = len(df)
    df.loc[length] = row
print(df)

main_content = df.to_json(orient="records")
df.to_excel('./combined_data.xlsx', index=False, sheet_name='report')
file = open("json_data.json", 'w')
file.write(main_content)
file.close()
