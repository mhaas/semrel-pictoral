
#include <opencv2/opencv.hpp>
#include "opencv2/features2d/features2d.hpp"
#include "opencv2/nonfree/nonfree.hpp"

#include <boost/filesystem.hpp>


#include <stdio.h>
#include <fstream>
#include <iostream>
#include <memory>
#include <functional>

using namespace std;
using namespace cv;

namespace fs = ::boost::filesystem;

BOWKMeansTrainer trainer = BOWKMeansTrainer(1000);

Mat* extractAndCompute(Mat img) {
    // detect keypoints
    SiftFeatureDetector detector(400);
    vector<KeyPoint> keypoints;
    detector.detect(img, keypoints);


    // computing descriptors
    SiftDescriptorExtractor extractor;
    Mat *descriptors;
    extractor.compute(img, keypoints, *descriptors);
    return descriptors;
}

void printMatrix(Mat m) {
    // Print it
    int rows = m.rows;
    int cols = m.cols;
    printf(" Matrix m: \n");
    for( size_t i = 0; i < rows; i++ ) {
         for( size_t j = 0; j < cols; j++ ) {
              // Observe the type used in the template
              printf( " %d  ", m.at<uchar>(i,j) );
         }
         printf("\n");
         printf("------\n");
    }
    printf("++++++++++++\n");

}


void printMatrixToFile(String fileName, Mat m) {
    int rows = m.rows;
    int cols = m.cols;
    FILE *fp;
    fp = fopen(fileName.c_str(), "w");
    fprintf(fp, "[");
    for( size_t i = 0; i < rows; i++ ) {
         for( size_t j = 0; j < cols; j++ ) {
              // Observe the type used in the template
              fprintf(fp,"%d,", m.at<uchar>(i,j) );
         }
    }
    fseek(fp, -1L, SEEK_CUR);
    fprintf(fp, "]");
    fclose(fp);
}


// return the filenames of all files that have the specified extension
// in the specified directory and all subdirectories
void get_all(const fs::path& root, const string& ext, vector<fs::path>& ret)
{  
  if (!fs::exists(root)) return;

  if (fs::is_directory(root))
  {
    fs::recursive_directory_iterator it(root);
    fs::recursive_directory_iterator endit;
    while(it != endit)
    {
      //printf("loop");
      //printf("%s", it->path().extension().c_str());
      if (fs::is_regular_file(*it) and it->path().extension() == ext)
        ret.push_back(it->path());
      ++it;
    }
  }
}


// taken from https://github.com/Itseez/opencv/blob/2.4/samples/cpp/bagofwords_classification.cpp
bool writeBowImageDescriptor( const string& file, const Mat& bowImageDescriptor )
{
    cv::FileStorage fs( file, cv::FileStorage::WRITE );
    if( fs.isOpened() )
    {
        fs << "imageDescriptor" << bowImageDescriptor;
        return true;
    }
    return false;
}

void normalizeMat(Mat& m) {

    for(int i = 0; i < m.rows; i++) {
        int* mi = m.ptr<int>(i);
        for(int j = 0; j < m.cols; j++) {
            if (mi[j] > 0)
                mi[j] = 1;
        }
    }
}

int main( int argc, const char* argv[] )
{
    if (argc < 2) {
        printf("not enough arguments\n");
        return -1;
    }

    printf("File: %s\n", argv[1]);
    String ext = ".img";
    vector<fs::path> files;
    fs::path p(argv[1]);
    get_all(p, ext, files);
    printf("files found: %d\n", files.size());
    

    for(std::vector<fs::path>::iterator it = files.begin(); it != files.end(); ++it) {
        String curFile = (*it).c_str();
        Mat img = imread(curFile, CV_LOAD_IMAGE_GRAYSCALE);
        ///Mat resized;
        //cv::resize(img, resized, cv::Size(640, 480), cv::INTER_AREA);
        if(img.empty())
        {
            printf("Can't read one of the images: %s\n", curFile.c_str());
            //return -1;
            continue;
        }
        Mat descriptors = *(extractAndCompute(img));
        printf("Got descriptors.\n");
        trainer.add(descriptors);
    }
    printf("Clustering..\n");
    Mat vocabulary = trainer.cluster();
    printf("Done clustering...\n");

    SiftFeatureDetector detector(400);
    SiftDescriptorExtractor extractor;

    Ptr<FeatureDetector> featureDetector = FeatureDetector::create( "SIFT" );
    Ptr<DescriptorExtractor> descExtractor = DescriptorExtractor::create( "SIFT" );
    Ptr<DescriptorMatcher> descMatcher = DescriptorMatcher::create( "FlannBased" );
    Ptr<BOWImgDescriptorExtractor> bowExtractor;

    //  C++: BOWImgDescriptorExtractor::BOWImgDescriptorExtractor(const Ptr<DescriptorExtractor>& dextractor, const Ptr<DescriptorMatcher>& dmatcher)
    bowExtractor = new BOWImgDescriptorExtractor( descExtractor, descMatcher );
    bowExtractor->setVocabulary(vocabulary);

    for(std::vector<fs::path>::iterator it = files.begin(); it != files.end(); ++it) {
        String curFile = (*it).c_str();
        Mat img = imread(curFile, CV_LOAD_IMAGE_GRAYSCALE);
        if(img.empty())
        {
            printf("Can't read one of the images: %s\n", curFile.c_str());
            //return -1;
            continue;
        }
        vector<KeyPoint> keyPoints;
        detector.detect(img, keyPoints);
        printf("Got feature vectors.\n");
        // descriptors expressed in voc terms, i.e. clusters
        Mat descriptors;
        //vector<vector<int> > *pointIdxsOfClusters;
        //Mat *origDescriptors;
        // C++: void BOWImgDescriptorExtractor::compute(const Mat& image, vector<KeyPoint>& keypoints, Mat& imgDescriptor, vector<vector<int>>* pointIdxsOfClusters=0, Mat* descriptors=0 )
        bowExtractor->compute(img, keyPoints, descriptors);//, pointIdxsOfClusters, origDescriptors);
        std::cout << "Size of vocabulary: " << vocabulary.size() << std::endl;
        std::cout << "Size of found visual words: " << descriptors.size() << std::endl;
        String fileName = curFile + ".bow";
        writeBowImageDescriptor(fileName, descriptors);
        printMatrixToFile(fileName + ".simple", descriptors);
        normalizeMat(descriptors);
        writeBowImageDescriptor(fileName + ".normalized", descriptors);
        printMatrixToFile(fileName + "normalized.simple", descriptors);

    }

 
}


