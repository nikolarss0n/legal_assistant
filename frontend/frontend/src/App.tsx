import { useState } from "react";
import styled from "@emotion/styled";
import { motion } from "framer-motion";
import TextInput from "./components/TextInput";
import ResponseCard from "./components/ResponseCard";
import UserQuery from "./components/UserQuery";
import { LegalResponse, searchLegalInfo } from "./services/api";

const AppContainer = styled.div`
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-x: hidden;
`;

const ContentContainer = styled.div`
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  padding-bottom: 4rem;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 3rem;
`;

const Title = styled(motion.h1)`
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  background: linear-gradient(to right, #ffffff, #a3a3ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  max-width: 600px;
  margin: 0 auto;
`;

const ResponsesContainer = styled.div`
  margin-top: 2rem;
`;

const InputContainer = styled.div`
  margin: 2rem 0;
`;

const BlurCircle = styled(motion.div)<{
	top: string;
	left: string;
	size: string;
	color: string;
}>`
  position: fixed;
  top: ${(props) => props.top};
  left: ${(props) => props.left};
  width: ${(props) => props.size};
  height: ${(props) => props.size};
  border-radius: 50%;
  background: ${(props) => props.color};
  filter: blur(80px);
  opacity: 0.4;
  z-index: -1;
`;

// Define a type for conversation entries
interface ConversationEntry {
	type: 'query' | 'response';
	content: string | LegalResponse;
}

function App() {
	const [loading, setLoading] = useState(false);
	const [conversation, setConversation] = useState<ConversationEntry[]>([]);

	const handleSubmit = async (text: string) => {
		setLoading(true);

		// Add the user query to the conversation
		setConversation((prev) => [...prev, { type: 'query', content: text }]);

		try {
			// Only use real backend with locally downloaded Gemma 3 model
			const response = await searchLegalInfo(text);
			
			// Add the response to the conversation
			setConversation((prev) => [...prev, { type: 'response', content: response }]);
		} catch (error) {
			console.error("Error getting response:", error);
		} finally {
			setLoading(false);
		}
	};

	return (
		<AppContainer>
			{/* Decorative blur circles */}
			<BlurCircle
				top="-10%"
				left="10%"
				size="500px"
				color="#4d5bce"
				animate={{
					x: [0, 50, 0],
					y: [0, 30, 0],
				}}
				transition={{
					repeat: Infinity,
					duration: 20,
					ease: "easeInOut",
				}}
			/>
			<BlurCircle
				top="60%"
				left="80%"
				size="400px"
				color="#cd5c5c"
				animate={{
					x: [0, -40, 0],
					y: [0, -20, 0],
				}}
				transition={{
					repeat: Infinity,
					duration: 15,
					ease: "easeInOut",
					delay: 2,
				}}
			/>
			<BlurCircle
				top="80%"
				left="5%"
				size="300px"
				color="#4e8d7c"
				animate={{
					x: [0, 30, 0],
					y: [0, -40, 0],
				}}
				transition={{
					repeat: Infinity,
					duration: 18,
					ease: "easeInOut",
					delay: 1,
				}}
			/>

			<ContentContainer>
				<Header>
					<Title
						initial={{ opacity: 0, y: -20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5 }}
					>
						Bulgarian Labor Law Assistant
						<br/>
						<span style={{ fontSize: "0.85em" }}>Асистент за Трудово Право</span>
					</Title>
					<Subtitle>
						Ask questions about Bulgarian labor law in English or Bulgarian
						<br/>
						Задавайте въпроси относно трудовото законодателство на български или английски
					</Subtitle>
				</Header>

				<InputContainer>
					<TextInput
						onSubmit={handleSubmit}
						loading={loading}
						placeholder="Ask about probation, leave, salary... / Питайте за изпитателен срок, отпуск, заплата..."
					/>
				</InputContainer>

				<ResponsesContainer>
					{conversation.map((entry, index) => {
						if (entry.type === 'query') {
							// For user queries, render the UserQuery component
							return <UserQuery key={`query-${index}`} query={entry.content as string} />;
						} else {
							// For responses, extract sections as before
							const response = entry.content as LegalResponse;
							let sections: string[] = [];
							
							// Check if the response contains section markers (in either language)
							const hasSectionMarkers = response.answer.includes('СЕКЦИЯ') || 
													  response.answer.includes('SECTION') ||
													  response.answer.includes('Секция') || 
													  response.answer.includes('Section');
							
							if (hasSectionMarkers) {
								// Define possible section markers (both languages, case variants)
								const sectionMarkersVariants = [
									// Bulgarian variations
									['СЕКЦИЯ 1:', 'СЕКЦИЯ 2:', 'СЕКЦИЯ 3:', 'СЕКЦИЯ 4:'],
									['Секция 1:', 'Секция 2:', 'Секция 3:', 'Секция 4:'],
									['СЕКЦИЯ 1.', 'СЕКЦИЯ 2.', 'СЕКЦИЯ 3.', 'СЕКЦИЯ 4.'],
									['Секция 1.', 'Секция 2.', 'Секция 3.', 'Секция 4.'],
									// English variations
									['SECTION 1:', 'SECTION 2:', 'SECTION 3:', 'SECTION 4:'],
									['Section 1:', 'Section 2:', 'Section 3:', 'Section 4:'],
									['SECTION 1.', 'SECTION 2.', 'SECTION 3.', 'SECTION 4.'],
									['Section 1.', 'Section 2.', 'Section 3.', 'Section 4.']
								];
								
								// Find which set of markers is in the text
								let foundMarkers = null;
								for (const markers of sectionMarkersVariants) {
									// Check if at least 3 of the 4 markers exist in the text
									const markerCount = markers.filter(m => response.answer.includes(m)).length;
									if (markerCount >= 3) {
										foundMarkers = markers;
										break;
									}
								}
								
								// If we found markers, use them to extract sections
								if (foundMarkers) {
									let tempAnswer = response.answer;
									sections = [];
									
									// Extract each section
									for (let i = 0; i < foundMarkers.length; i++) {
										const currentMarker = foundMarkers[i];
										const nextMarker = foundMarkers[i + 1];
										
										if (tempAnswer.includes(currentMarker)) {
											let sectionText = '';
											
											if (nextMarker && tempAnswer.includes(nextMarker)) {
												// Extract between current and next marker
												sectionText = tempAnswer.substring(
													tempAnswer.indexOf(currentMarker) + currentMarker.length,
													tempAnswer.indexOf(nextMarker)
												).trim();
												
												// Remove the processed part
												tempAnswer = tempAnswer.substring(tempAnswer.indexOf(nextMarker));
											} else {
												// Last section or only one section
												sectionText = tempAnswer.substring(
													tempAnswer.indexOf(currentMarker) + currentMarker.length
												).trim();
											}
											
											sections.push(sectionText);
										}
									}
								}
							}
							
							// If we couldn't parse sections, use the whole answer as one section
							if (sections.length === 0) {
								sections = [response.answer];
							}
							
							return (
								<div key={`response-${index}`}>
									{/* Display structured sections if available */}
									{sections.map((sectionContent, sectionIndex) => (
										<ResponseCard 
											key={`response-${index}-section-${sectionIndex + 1}`}
											content={sectionContent}
											section={sections.length > 1 ? sectionIndex + 1 : undefined}
										/>
									))}
									
									{/* Display articles only if there are no structured sections or explicitly requested */}
									{(sections.length <= 1 || sections.some(s => s.includes('законов текст') || s.includes('legal text'))) && 
									  response.articles.map((article, artIndex) => (
										<ResponseCard 
											key={`response-${index}-article-${artIndex}`}
											isArticle
											articleNumber={article.number}
											title={article.title}
											content={article.content}
										/>
									))}
								</div>
							);
						}
					})}
				</ResponsesContainer>
			</ContentContainer>
		</AppContainer>
	);
}

export default App;