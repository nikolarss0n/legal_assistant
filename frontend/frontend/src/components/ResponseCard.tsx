import styled from '@emotion/styled';
import { motion } from 'framer-motion';
import GlassCard from './GlassCard';

interface ResponseCardProps {
  isArticle?: boolean;
  articleNumber?: string;
  title?: string;
  content: string;
  section?: number;
}

const ArticleHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
`;

const ArticleNumber = styled.div`
  background: rgba(255, 255, 255, 0.15);
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  margin-right: 1rem;
  font-size: 0.9rem;
`;

const Title = styled.h3`
  margin: 0;
  font-weight: 500;
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
`;

const Content = styled.div`
  font-size: 1rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  
  p {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ResponseContainer = styled(motion.div)`
  margin-bottom: 1.5rem;
`;

const SectionLabel = styled.div`
  background: rgba(255, 255, 255, 0.15);
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  align-self: flex-start;
`;

const ResponseCard: React.FC<ResponseCardProps> = ({ 
  isArticle = false,
  articleNumber,
  title,
  content,
  section
}) => {
  // Section labels in Bulgarian and English
  const sectionLabels: Record<number, { bg: string, en: string }> = {
    1: { bg: 'Приложими членове', en: 'Applicable Articles' },
    2: { bg: 'Обобщение', en: 'Summary' },
    3: { bg: 'Законов текст', en: 'Legal Text' },
    4: { bg: 'Последици и препоръки', en: 'Consequences and Recommendations' }
  };

  // Determine if we're displaying in Bulgarian based on content
  const isBulgarian = /[а-яА-Я]/.test(content);
  
  return (
    <ResponseContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <GlassCard>
        {section && section > 0 && section <= 4 && (
          <SectionLabel>
            {isBulgarian ? sectionLabels[section].bg : sectionLabels[section].en}
          </SectionLabel>
        )}
        
        {isArticle && (
          <ArticleHeader>
            {articleNumber && (
              <ArticleNumber>
                {isBulgarian ? `Член ${articleNumber}` : `Article ${articleNumber}`}
              </ArticleNumber>
            )}
            {title && <Title>{title}</Title>}
          </ArticleHeader>
        )}
        
        <Content>
          {content.split('\n').map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </Content>
      </GlassCard>
    </ResponseContainer>
  );
};

export default ResponseCard;