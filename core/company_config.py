"""
Company Configuration Loader
Reads company branding and details from company_config.ini
"""

import configparser
import os

class CompanyConfig:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompanyConfig, cls).__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        cls._config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'company_config.ini')
        
        if os.path.exists(config_path):
            cls._config.read(config_path, encoding='utf-8')
        else:
            # Create default config
            cls._config['Company'] = {
                'logo_path': '',
                'name_en': 'PHONIX ENTERPRISE',
                'address_en': '123 Business Street, City, Country',
                'phone_en': '+1 (555) 123-4567',
                'email_en': 'info@phonixenterprise.com',
                'tax_id_en': 'TAX-123456789',
                'name_ar': 'فونكس انتربرايز',
                'address_ar': '١٢٣ شارع الأعمال، المدينة، الدولة',
                'phone_ar': '+١ (٥٥٥) ١٢٣-٤٥٦٧',
                'email_ar': 'info@phonixenterprise.com',
                'tax_id_ar': 'TAX-123456789'
            }
            cls._config['Invoice'] = {
                'prefix': 'INV',
                'terms_en': 'Payment is due within 30 days.',
                'terms_ar': 'الدفع مستحق خلال ٣٠ يوماً.',
                'payment_en': 'Bank Transfer: Account #123456789',
                'payment_ar': 'تحويل بنكي: حساب رقم ١٢٣٤٥٦٧٨٩'
            }
    
    @classmethod
    def get(cls, section, key, fallback=''):
        if cls._config is None:
            cls._load_config()
        return cls._config.get(section, key, fallback=fallback)
    
    @classmethod
    def get_company_info(cls, lang='en'):
        """Get all company info for a specific language"""
        suffix = '_' + lang
        return {
            'name': cls.get('Company', f'name{suffix}'),
            'address': cls.get('Company', f'address{suffix}'),
            'phone': cls.get('Company', f'phone{suffix}'),
            'email': cls.get('Company', f'email{suffix}'),
            'tax_id': cls.get('Company', f'tax_id{suffix}'),
            'logo_path': cls.get('Company', 'logo_path')
        }
    
    @classmethod
    def get_invoice_info(cls, lang='en'):
        """Get invoice settings for a specific language"""
        suffix = '_' + lang
        return {
            'prefix': cls.get('Invoice', 'prefix'),
            'terms': cls.get('Invoice', f'terms{suffix}'),
            'payment': cls.get('Invoice', f'payment{suffix}')
        }
