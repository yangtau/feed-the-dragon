import page_manager 
import start_page


def main():
    pm = page_manager.PageManager((808, 700), 'Hello')
    sp = start_page.StartPage(pm)
    pm.push(sp)
    pm.run()

if __name__ == '__main__':
    main()
