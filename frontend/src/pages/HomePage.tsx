import { Link } from 'react-router-dom';
import { Tag, ArrowRight, Database, Ban } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

const features = [
  {
    icon: Tag,
    title: 'Keywords',
    description: 'Manage English and Spanish search keywords for scraping.',
    to: '/keywords',
  },
  {
    icon: Ban,
    title: 'Stopwords',
    description: 'Define terms to filter out from scraped results.',
    to: '/stopwords',
  },
  {
    icon: Database,
    title: 'Listings',
    description: 'Browse, save, and manage scraped cigar listings.',
    to: '/data',
  },
];

const HomePage = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
      <div className="mb-12">
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-zinc-900 mb-3">
          Cigar Listing Scraper
        </h1>
        <p className="text-base text-zinc-500 max-w-xl leading-relaxed">
          Manage keywords, filter stopwords, and review scraped listings from multiple marketplaces.
        </p>
        <div className="mt-6">
          <Link to="/keywords">
            <Button size="lg">
              Manage Keywords
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {features.map(({ icon: Icon, title, description, to }) => (
          <Link key={to} to={to} className="group">
            <Card className="h-full hover:border-zinc-300 transition-colors">
              <div className="flex items-center justify-center w-9 h-9 rounded-md bg-zinc-100 mb-4 group-hover:bg-zinc-200 transition-colors">
                <Icon className="w-4 h-4 text-zinc-600" />
              </div>
              <h2 className="text-sm font-semibold text-zinc-900 mb-1">{title}</h2>
              <p className="text-sm text-zinc-500 leading-relaxed">{description}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
