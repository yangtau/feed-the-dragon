import page_manager 
import start_page
import common


def main():
    pm = page_manager.PageManager(common.WIN_SIZE, '拯救大魔王')
    sp = start_page.StartPage(pm)
    pm.push(sp)
    pm.run()

if __name__ == '__main__':
    main()
