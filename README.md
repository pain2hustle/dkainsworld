# DKAINSWORLD

Dylan's secondhand store website: **https://dkainsworld.pages.dev/**

Tools, boards, furniture, backpacks and flea-market finds in Fremont, CA.
Call or text (510) 435-0747 · dkain1017dk@gmail.com

## What's in here

| Folder / file | What it is |
|---|---|
| `site/` | The live website, exactly as it's published. Open `site/index.html` in a browser to see it. |
| `inventory.csv` | Every item, its price and description. Opens in Excel or Google Sheets. |
| `inventory.json` | The same item list, in the format the site builder reads. |
| `source/` | The builder script and style files that make `site/`. |

## Changing prices or items

1. Open `inventory.csv` in Google Sheets or Excel.
2. Change the `price_text` or `description` column, or add a new row.
3. Save it, and send it to Austin, or commit it here on GitHub.
4. The site is rebuilt from that file, so the item cards, the "Every item and price" list and `llms.txt` all update together.

Quick text fixes can also be made right in `site/index.html` with GitHub's edit (pencil) button.

## Photos

Item photos live in `site/assets/items/`. Name a new photo after the item (for example `couches-1.jpg`), upload it there, and add its path in the `photos` column of `inventory.csv`.

## Store terms (shown on the site)

- All items are sold as-is. Inspect the item before paying; paying means you accept it.
- Contact Dylan within 1 hour of buying if there's a problem. All sales are final.
- Store credit may be possible the same day if the item is unused and still works the same. Not guaranteed.

## Payments

- Zelle: (510) 435-0747 or dkain1017dk@gmail.com
- Cash App and PayPal: dkain1017dk@gmail.com
- Chime: ask Dylan

---
Website built by [Artificial Mind Hive](https://artificialmindhive.com/).
