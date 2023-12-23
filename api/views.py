from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Image, Annotation
from api.serializers import ImageSerializer, AnnotationSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ImageAnnotationView(APIView):
    def get(self, request, pk, format=None):
        annotation = Annotation.objects.filter(image_id=pk)
        serializer = AnnotationSerializer(annotation, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        image = get_object_or_404(Image, pk=pk)
        data = request.data
        if isinstance(data, list):
            for i, annotation in enumerate(data):
                if "relations" not in annotation:
                    data[i]["image"] = image.pk
            serializer = AnnotationSerializer(data=data, many=True)
        else:
            data["image"] = image.pk
            serializer = AnnotationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


class AnnotationDetailView(APIView):
    def get(self, request, pk, format=None):
        annotation = Annotation.objects.get(pk=pk)
        serializer = AnnotationSerializer(annotation)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        annotation = Annotation.objects.get(pk=pk)
        serializer = AnnotationSerializer(annotation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
