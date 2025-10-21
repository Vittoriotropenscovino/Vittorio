import React, { useRef, useState } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  Dimensions,
  Text,
  ViewToken,
} from 'react-native';
import { TravelMemory } from '../types/TravelMemory';
import { MemoryCard } from './MemoryCard';

interface MemoryGalleryProps {
  memories: TravelMemory[];
}

const { width } = Dimensions.get('window');

export const MemoryGallery: React.FC<MemoryGalleryProps> = ({ memories }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      if (viewableItems.length > 0 && viewableItems[0].index !== null) {
        setCurrentIndex(viewableItems[0].index);
      }
    }
  ).current;

  const viewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50,
  }).current;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>I Miei Ricordi di Viaggio</Text>
        <Text style={styles.counter}>
          {currentIndex + 1} / {memories.length}
        </Text>
      </View>
      <FlatList
        ref={flatListRef}
        data={memories}
        renderItem={({ item }) => <MemoryCard memory={item} />}
        keyExtractor={(item) => item.id}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        snapToAlignment="center"
        decelerationRate="fast"
        snapToInterval={width * 0.85 + 20}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    paddingTop: 40,
    paddingHorizontal: 20,
    paddingBottom: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  counter: {
    fontSize: 18,
    color: '#999',
  },
  listContent: {
    paddingLeft: (width - width * 0.85) / 2 - 10,
    paddingRight: (width - width * 0.85) / 2 - 10,
  },
});
