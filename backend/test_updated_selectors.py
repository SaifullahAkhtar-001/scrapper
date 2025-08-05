#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
from scrapers.todocoleccion_scraper import TodocoleccionScraper

def test_updated_selectors():
    """Test the updated selectors with the provided HTML snippet"""
    
    # HTML snippet provided by the user
    html_snippet = '''
    <div class="_lote_items _lote_items-as-list">
        <div class="_lote_item" data-id-lote="47047721">
            <div class="_lote_item-image-and-content">
                <div class="follow-lote-button lotes-enlaces-rapidos mr-0 mr-md-1">
                    <button class="d-flex justify-content-center align-items-center text-brand bg-white border-0 rounded-circle lotes_enlaces_rapidos-button btn-circle clickeable isnt-active js-followup ga-track-click-in-poner-en-seguimiento" id="corazon-47047721" onclick="" data-ajax="/api/seguimientos/create?id=47047721" data-require-login="true" data-id_lote="47047721" data-nuevo-usuario-accion-tipo="0" data-nuevo-usuario-accion-valor="47047721" rel="nofollow" title="Seguir" type="button">
                        <i class="bi lotes_enlaces_rapidos-icon js-icon-seguimiento inline-block bi-heart"></i>
                    </button>
                </div>
                <div class="_lote_item-content">
                    <div class="_lote_item-image">
                        <div class="_lote_item-img-main-container">
                            <a href="/coleccionismo-puros/caja-antigua-puros-gulden-eeuw-10-senoritas-completa-10-puros-cigarrillos-cigarros-paquete~x47047721#ofertas_al_vendedor" title="Hacer oferta al vendedor" class="_lote_item-img-footerbox _lote_item-img-footerbox-admite_ofertas ga-track-click-in-lote_item-footerbox-admite_ofertas">
                                <i class="icon icon-exchange"></i> &nbsp; Admite ofertas
                            </a>
                            <a data-id-lote="47047721" data-image-url="https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.webp" class="ga-track-click-buscador _lote_item-img-main-link text-gray-500 js-over_image" href="/coleccionismo-puros/caja-antigua-puros-gulden-eeuw-10-senoritas-completa-10-puros-cigarrillos-cigarros-paquete~x47047721">
                                <picture>
                                    <source type="image/webp" srcset="https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.webp?size=158x158&amp;crop=true 158w,https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.webp?size=200x200&amp;crop=true 200w,https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.webp?size=230x230&amp;crop=true 230w" sizes="(max-width: 767px) 158px, ((min-width: 768px) and (max-width: 991px)) 200px, 230px">
                                    <img src="https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.jpg?size=230x230&amp;crop=true" title="CAJA ANTIGUA DE PUROS - GULDEN EEUW 10 SENORITAS - COMPLETA 10 PUROS - CIGARRILLOS CIGARROS PAQUETE" alt="Cajas de Puros: CAJA ANTIGUA DE PUROS - GULDEN EEUW 10 SENORITAS - COMPLETA 10 PUROS - CIGARRILLOS CIGARROS PAQUETE" width="230" height="230" sizes="(max-width: 767px) 158px, ((min-width: 768px) and (max-width: 991px)) 200px, 230px" srcset="https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.jpg?size=158x158&amp;crop=true 158w,https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.jpg?size=200x200&amp;crop=true 200w,https://cloud10.todocoleccion.online/coleccionismo-puros/tc/2015/01/04/21/47047721.jpg?size=230x230&amp;crop=true 230w" class="_lote_item-img-main thumb-lote-foto media-object img-fluid rounded">
                                </picture>
                            </a>
                            <div id="foto47047721" class="full-size d-none d-lg-block d-xl-block">
                            </div>
                        </div>
                    </div>
                    <div class="_lote_content-body">
                        <h2 class="_lote_item-titulo font-weight-normal fs-14 fs-sm-16 fs-lg-18">
                            <a id="lot-title-47047721" href="/coleccionismo-puros/caja-antigua-puros-gulden-eeuw-10-senoritas-completa-10-puros-cigarrillos-cigarros-paquete~x47047721" class="ga-track-click-buscador js-lot-titles block text-gray-900" title="Caja antigua de puros - gulden eeuw 10 senoritas - completa 10 puros -">
                                CAJA ANTIGUA DE PUROS - GULDEN EEUW 10 SENORITAS - COMPLETA 10 PUROS - CIGARRILLOS CIGARROS PAQUETE
                            </a>
                        </h2>
                        <p class="_lote_item-section text-gray-700">
                            <a class="text-gray-700" href="/buscador?bu=cigarro%20antiguo&amp;sec=cajas%2Dpuros&amp;O=rl">
                                Cajas de Puros antiguos y de colección
                            </a>
                        </p>
                        <p class="lote-vendedor d-none d-sm-block">
                            <span class="fs-14 text-gray-700" title="Vendedor AUTOMOBILIA">AUTOMOBILIA</span> &nbsp;
                            <span title="5 sobre 5">
                                <i class="bi text-sell-600 mx-2 bi-star-fill"></i><i class="bi text-sell-600 mx-2 bi-star-fill"></i><i class="bi text-sell-600 mx-2 bi-star-fill"></i><i class="bi text-sell-600 mx-2 bi-star-fill"></i><i class="bi text-sell-600 mx-2 bi-star-fill"></i>
                            </span>
                            <span class="text-gray-600" title="16161 valoraciones recibidas">
                                <small>(16.161)</small>
                            </span>
                        </p>
                        <div>
                            <span class="_lote_item-margin-right">
                                <span class="text-nowrap precio-lote-listado _lote_item-precio fs-18 fs-sm-24 _lote_item-margin-right text-gray-900">
                                    15,00 €
                                </span>
                            </span>
                            <div>
                            </div>
                        </div>
                    </div>
                    <div class="_lote-content-bottom">
                        <div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="_lote_item-separator">
            </div>
        </div>
    </div>
    '''
    
    # Create scraper instance
    scraper = TodocoleccionScraper()
    
    # Parse the HTML
    soup = BeautifulSoup(html_snippet, 'html.parser')
    
    # Find the listing element
    listing_element = soup.select_one('div._lote_item')
    
    if not listing_element:
        print("❌ Could not find listing element with selector 'div._lote_item'")
        return
    
    print("✅ Found listing element")
    
    # Test title extraction
    title = scraper._extract_title(listing_element)
    print(f"📝 Title: {title}")
    
    # Test price extraction
    price = scraper._extract_price(listing_element)
    print(f"💰 Price: {price}")
    
    # Test URL extraction
    url = scraper._extract_url(listing_element)
    print(f"🔗 URL: {url}")
    
    # Test image extraction
    images = scraper._extract_images(listing_element)
    print(f"🖼️ Images: {images}")
    
    # Test description extraction
    description = scraper._extract_description(listing_element)
    print(f"📄 Description: {description}")
    
    # Test full listing extraction
    listing_data = scraper._extract_single_listing(listing_element, "test_keyword")
    if listing_data:
        print("\n📋 Full Listing Data:")
        for key, value in listing_data.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Failed to extract listing data")

if __name__ == "__main__":
    test_updated_selectors() 