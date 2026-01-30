import React from 'react';
import { View, Text, Image, StyleSheet, Dimensions } from 'react-native';
import { TravelMemory } from '../types/TravelMemory';

interface MemoryCardProps {
  memory: TravelMemory;
}

const { width, height } = Dimensions.get('window');

export const MemoryCard: React.FC<MemoryCardProps> = ({ memory }) => {
  const renderStars = (rating: number) => {
    return '⭐'.repeat(rating);
  };

  return (
    <View style={styles.card}>
      <Image
        source={{ uri: memory.imageUrl }}
        style={styles.image}
        resizeMode="cover"
      />
      <View style={styles.overlay}>
        <View style={styles.content}>
          <Text style={styles.destination}>{memory.destination}</Text>
          <Text style={styles.country}>{memory.country}</Text>
          <Text style={styles.date}>{new Date(memory.date).toLocaleDateString('it-IT', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
          })}</Text>
          <Text style={styles.description}>{memory.description}</Text>
          <Text style={styles.rating}>{renderStars(memory.rating)}</Text>
          <View style={styles.tagsContainer}>
            {memory.tags.map((tag, index) => (
              <View key={index} style={styles.tag}>
                <Text style={styles.tagText}>#{tag}</Text>
              </View>
            ))}
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    width: width * 0.85,
    height: height * 0.9,
    marginHorizontal: 10,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#000',
  },
  image: {
    width: '100%',
    height: '100%',
    position: 'absolute',
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'flex-end',
  },
  content: {
    padding: 20,
    paddingBottom: 30,
  },
  destination: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  country: {
    fontSize: 22,
    color: '#f0f0f0',
    marginBottom: 8,
  },
  date: {
    fontSize: 16,
    color: '#d0d0d0',
    marginBottom: 12,
  },
  description: {
    fontSize: 16,
    color: '#fff',
    lineHeight: 22,
    marginBottom: 12,
  },
  rating: {
    fontSize: 20,
    marginBottom: 10,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginRight: 8,
    marginBottom: 8,
  },
  tagText: {
    color: '#fff',
    fontSize: 14,
  },
});
