from django.http import JsonResponse
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    parser_classes,
)
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import status
from .models import CompanyRegistration, Offers, placementNotice, jobAcceptance
from .serializers import (
    CompanyRegistrationSerializer,
    OffersSerializer,
    PlacementNoticeSerializer,
    JobAcceptanceSerializer,
    JobApplicationSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from base.models import User
from django.views.decorators.csrf import csrf_exempt
from student.models import Student
from .models import jobApplication
from uuid import uuid4
from student.serializers import StudentSerializer
from rest_framework.exceptions import NotFound
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from uuid import uuid4


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_company_with_offers(request, pk=None):
    try:
        if pk:
            # Retrieve a specific company and its offers
            company = CompanyRegistration.objects.get(id=pk)
            company_serializer = CompanyRegistrationSerializer(company)
            offers = Offers.objects.filter(company=company)
            offers_serializer = OffersSerializer(offers, many=True)

            return JsonResponse(
                {
                    "company": company_serializer.data,
                    "offers": offers_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Retrieve all companies with their offers
            companies = CompanyRegistration.objects.all()
            response_data = []
            for company in companies:
                company_serializer = CompanyRegistrationSerializer(company)
                offers = Offers.objects.filter(company=company)
                offers_serializer = OffersSerializer(offers, many=True)

                response_data.append(
                    {
                        "company": company_serializer.data,
                        "offers": offers_serializer.data,
                    }
                )

            return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)
    except CompanyRegistration.DoesNotExist:
        return JsonResponse(
            {"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_all_companies(request):
    try:
        companies = CompanyRegistration.objects.all()
        company_data = []
        for company in companies:
            company_serializer = CompanyRegistrationSerializer(company)
            offers = Offers.objects.filter(company=company)
            offers_serializer = OffersSerializer(offers, many=True)
            company_data.append(
                {"company": company_serializer.data, "offers": offers_serializer.data}
            )
        return JsonResponse(company_data, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_notice(request, pk):
    try:
        company = CompanyRegistration.objects.get(id=pk)
        data = JSONParser().parse(request)
        if not company:
            return JsonResponse(
                {"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND
            )
        notice_data = data
        print(notice_data)
        notice_data["company"] = company
        placement_notice = placementNotice.objects.create(**notice_data)
        return JsonResponse(
            {"message": "Notice created successfully"}, status=status.HTTP_201_CREATED
        )

    except CompanyRegistration.DoesNotExist:
        # Handle case where company does not exist
        return JsonResponse(
            {"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        # Handle any other exception and return the error
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def company_register(request, safe):
    try:
        data = request.data
        print(data)
        company_data = data.get("company")
        company_serializer = CompanyRegistrationSerializer(data=company_data)
        if company_serializer.is_valid():
            company = company_serializer.save()
            print(company)
        else:
            return JsonResponse(
                company_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        # Create Offers
        offers_data = data.get("offers", [])
        for offer_data in offers_data:
            offer_data["company"] = company
            try:
                Offers.objects.create(**offer_data)
            except:
                pass
        return JsonResponse(
            {
                "message": "Company and related offers created successfully!",
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_notice(request, pk):
    try:
        notice = placementNotice.objects.get(id=pk)
        notice_data = PlacementNoticeSerializer(notice).data
        return JsonResponse(notice_data, status=status.HTTP_200_OK)
    except placementNotice.DoesNotExist:
        return JsonResponse(
            {"error": "Notice not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def job_application(request, pk):
    try:
        user = User.objects.get(email=request.user.email)
        student = Student.objects.get(user=user)
        company = CompanyRegistration.objects.get(pk=pk)
        jobApplication.objects.create(student=student, company=company, id=uuid4())
        return JsonResponse(
            {"success": "Job application submitted successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_student_application(request, uid):
    try:
        student = Student.objects.get(uid=uid)
    except Student.DoesNotExist:
        raise NotFound("Student not found.")

    serializer = StudentSerializer(student)
    return JsonResponse({"student": serializer.data}, safe=False)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_all_applied_students(request, pk):
    try:
        company = jobApplication(pk=pk)
        students = JobApplicationSerializer(company)
        return JsonResponse({"students": students.data})
    except Exception as e:
        print(e)
        return JsonResponse(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_job_acceptance(request):
    user = User.objects.get(email=request.user.email)
    if not user:
        return JsonResponse(
            {"error": "Failed to find user"}, status=status.HTTP_404_NOT_FOUND
        )
    student = Student.objects.get(user=user)
    company = None
    required_fields = ["type", "salary", "position"]
    for field in required_fields:
        if field not in request.data:
            return JsonResponse(
                {"error": f"Missing required field: {field}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if "offer_letter" not in request.FILES:
        return JsonResponse(
            {"error": "Offer letter file is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    job_acceptance = jobAcceptance.objects.create(
        id=uuid4(),
        student=student,
        company=None,
        company_name=request.data["company_name"][
            0
        ],  # Assuming company has company_name field
        offer_letter=request.FILES["offer_letter"],
        type=request.data["type"][0],
        salary=float(request.data["salary"][0]),
        position=request.data["position"][0],
        isVerified=False,  # Default value
    )
    return JsonResponse({"success": "Job application created"})


@authentication_classes([SessionAuthentication, BasicAuthentication])
@api_view(["GET"])
def get_job_acceptance_by_id(request, pk):
    try:
        job_acceptance = jobAcceptance.objects.get(id=pk)
    except jobAcceptance.DoesNotExist:
        return JsonResponse(
            {"error": "Job acceptance not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = JobAcceptanceSerializer(job_acceptance)
    return JsonResponse(serializer.data)


@api_view(["GET"])
def get_jobs_by_company_name(request, company_name):
    jobs = jobAcceptance.objects.filter(company_name=company_name)
    if not jobs.exists():
        return JsonResponse(
            {"error": "No jobs found for this company name."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = JobAcceptanceSerializer(jobs, many=True)
    return JsonResponse(serializer.data)


class JobAcceptanceView(APIView):
    def get(self, request):
        jobs = jobAcceptance.objects.all()
        serializer = JobAcceptanceSerializer(jobs, many=True)
        return JsonResponse(serializer.data)


@api_view(["POST"])
def verify_job(request, job_id):
    try:
        job = verify_job.objects.get(id=job_id)
        job.verified = True
        job.save()
        return JsonResponse(
            {"message": "Job verified successfully"}, status=status.HTTP_200_OK
        )
    except jobAcceptance.DoesNotExist:
        return JsonResponse(
            {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
        )
