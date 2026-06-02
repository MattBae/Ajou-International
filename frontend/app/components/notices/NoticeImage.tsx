import { useEffect, useState } from 'react';
import {
  Image,
  LayoutChangeEvent,
  StyleProp,
  StyleSheet,
  View,
  ViewStyle,
} from 'react-native';

type NoticeImageProps = {
  uri: string;
  style?: StyleProp<ViewStyle>;
  fallbackHeight?: number;
  maxHeight?: number;
};

export function NoticeImage({
  uri,
  style,
  fallbackHeight = 220,
  maxHeight,
}: NoticeImageProps) {
  const [containerWidth, setContainerWidth] = useState(0);
  const [aspectRatio, setAspectRatio] = useState<number | null>(null);

  useEffect(() => {
    let isMounted = true;

    Image.getSize(
      uri,
      (width, height) => {
        if (!isMounted || width <= 0 || height <= 0) return;
        setAspectRatio(width / height);
      },
      () => {
        if (isMounted) setAspectRatio(null);
      }
    );

    return () => {
      isMounted = false;
    };
  }, [uri]);

  const handleLayout = (event: LayoutChangeEvent) => {
    setContainerWidth(event.nativeEvent.layout.width);
  };

  const naturalHeight =
    containerWidth > 0 && aspectRatio ? containerWidth / aspectRatio : fallbackHeight;
  const height = maxHeight ? Math.min(naturalHeight, maxHeight) : naturalHeight;

  return (
    <View onLayout={handleLayout} style={[styles.container, style, { height }]}>
      <Image source={{ uri }} style={styles.image} resizeMode="contain" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    overflow: 'hidden',
    backgroundColor: '#F8FAFC',
  },
  image: {
    width: '100%',
    height: '100%',
  },
});
