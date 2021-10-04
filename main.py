import click, logging
from cool_ct import CTScan

LOGGER_NAME = 'ct_cli'

l = logging.getLogger(LOGGER_NAME)

@click.command()
@click.argument('img_path')
@click.option('--span', default=30)
@click.option('--increment', default=2)
@click.option('--n', default=180)
@click.option('--dbg-image', default=False)
def main(img_path, span, increment, n, dbg_image):
    logging.basicConfig(format="[%(asctime)s] %(levelname)-8s| %(lineno)s >> %(message)s")

    logging_modules = [LOGGER_NAME, 'ct', 'edp_trace']

    for module in logging_modules:
        logging.getLogger(module).setLevel(logging.DEBUG)
    
    c = CTScan(
            image_path=img_path, 
            span=span, 
            angle_increment=increment, 
            n=n, 
            t=True,
            dbg_image=dbg_image
            )

    l.info(f"width x height, radius: {c.width}x{c.height}, {c.radius}")

    c.make_sinogram()
    c.make_ct()

if __name__ == '__main__':
    main()
