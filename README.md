IMAGE CRUD

WHAT IS IT?
  IMAGE CRUD is a simple proof-of-concept web application. 
  The purpose of the app is to play around the new services in Eucalyptus 3.3 (AutoScaling, ELB, CloudWatch).
  The app allows you to upload, download, and delete photos to/on the service. For example, you can upload a photo to the service using the client tool:
  
  ./upload.py ../sample/cat1.jpeg http://localhost/imagecrud/afdef75e0376bddfd

  To upload the bulk of pictures in the sample directory:
  ./upload_many.py -c 10 ../sample/ http://localhost/imagecrud/

  You can browse the pictures by pointing your web browser at http://{IP_ADDRESS}/imagecrud/

APPLICATION ARCHITECTURE
  There are two types of application data to manage:
  1) picture file: the file is stored in Walrus and the application simply returns <img> tag with the url pointing to the Walrus url
  2) picture metadata: name of the picture, Walrus URL of the picure, etc

  While the picture file is stored in Walrus, the metadata is stored in EBS volume, which is made available via MySQL running on Eucalyptus VM.
  There can be multiple web services running the IMAGE CRUD (behind ELB), and each service will connect to MySQL instance runnning on a VM so that services
  can share the state in database.

SETUP
  1. MySQL instance
    1.1. create a new EBS volume
         euca-create-volume -s 10 -z PARTI00
    1.2. launch a VM instance (here we assume the Centos 6 as VM image) and attach the volume to the instance
         euca-run-instances -k mykey -t m1.large emi-144C36A2
         euca-attach-volume -i i-D7F6416E -d /dev/vdf  vol-1D4141B5
    1.3. mount the volume and create file system on it
         fdisk /dev/vdb (use 'n' and 'w' to create a new partition on it)
         mkfs.ext3 /dev/vdb1
         mkdir /opt/mysql
         mount /dev/vdb1 /opt/mysql/     
    1.4. Install MySQL srever
         yum install mysql-server
    1.5. Configure MySQL
         Open /etc/my.cnf and update the setting as follows:
         ------------------------------------------ 
         [mysqld]
           datadir=/opt/mysql/data
           socket=/var/lib/mysql/mysql.sock
           user=mysql
           # Disabling symbolic-links is recommended to prevent assorted security risks
           symbolic-links=0

         [mysqld_safe]
           log-error=/opt/mysql/log/mysqld.log
           pid-file=/var/run/mysqld/mysqld.pid
        --------------------------------------------
        Create directories to store MySQL data
        mkdir /opt/mysql/log
        mkdir /opt/mysql/data
        chown mysql:mysql /opt/mysql -R
    1.6. Start MySQL
        /etc/init.d/mysql start
    1.7. Create a 'euca' user which will be user to connect from the web application
        mysql
        create user 'euca'@'%' identified by 'foobar';
        grant all privileges on *.* to 'euca'@'%' with grant option;
        flush privileges;
        exit;
    1.8. Create a new 'eucapp' database to be used by application
        create database eucapp

    1.9. Open mysql's port '3306' on the security group
         euca-authorize -P tcp -p 3306 -s 0.0.0.0/0 default 

    1.10. You may want to create the EMI off the MySQL instance so that you can setup new VM quickly when the previous one dies.
         use 'euca-bundle-vol' to do it.

  2. Setup Django instance
    2.1. Launch a new Centos 6 VM
        euca-run-instances -k mykey -z PARTI00 -t m1.small emi-144C36A2
    2.2. Log-in the VM and install Python-Django
        yum install python-pip (epel repo)
        pip-python install Django 
    2.3. clone IMAGE CRUD from github at /opt/eucalyptopotamus
        cd /opt
        git clone https://github.com/eucalyptus/eucalyptopotamus
        cd /opt/eucalyptopotamus/django/eucapp
    2.4. Change settings
        Open eucapp/settings.py
        Change HOST under DATABASES to point to the IP address of the MySQL instance
        Also change Walrus URL, access_key and secret_key in IMAGECRUD dictionary (at the end of settings.py)
    2.5. Install Apache, mod_wsgi, and MySQL python library
        yum install httpd mod_wsgi MySQL-python
    2.6 Initialize database (create a bunch of Django default tables)
        /opt/eucalyptopotamus/django/eucapp
        python manage.py syncdb
    2.7 Symlink httpd.conf in the eucapp directory
        mv /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf.bkup
        ln -s /opt/eucalyptopotamus/django/eucapp/httpd.conf /etc/httpd/conf/httpd.conf
    2.8 Start httpd
        /etc/init.d/httpd start

USAGE
    Under client directory, you will find the command lines to interact with the service:
    ./upload_many.py -c 10 ../sample/ http://localhost/imagecrud/
    You can point your browser at the {IP}/imagecrud/ to see the pictures. To delete them,
    ./delete_all.py http://localhost/imagecrud/

SETUP WITH AUTOSCALING and ELB
    When the stand-alone service is running, you can scale-out the service using AS group and ELB.
    Here're the simple steps to do it:

    1. Create launch config
      1.1. Make sure httpd automatically starts when the VM boots
         chkconfig httpd on
      1.2. Create a new EMI off the VM running Django  (inside the VM)
         euca-bundle-vol -e /mnt/ -p django-05 -d ./bundle -r x86_64 -s 4096 --kernel eki-2EF33B3E --ramdisk eri-D6AB387F
         euca-upload-bundle -b django-05 -m ./bundle/django-05.manifest.xml 
         euca-register django-05/django-05.manifest.xml -n django05
      1.3. Create a launch config with the created EMI
         euscale-create-launch-config -i emi-98B93CD6 -t m1.small --key mykey imagecrud 

    2. Create ELB
      eulb-create-lb -l "lb-port=80, protocol=HTTP, instance-port=80" -z PARTI00 imagecrud

    3. Create autoscaling group associated with the ELB
      euscale-create-auto-scaling-group -l imagecrud -M 10 -m 1 --desired-capacity 1 --load-balancers imagecrud -z PARTI00 imagecrud      
    
    4. Make sure the new VMs are launched as part of the autoscaling group
      euscale-describe-scaling-activities 

    5. Wait until the launched VMs are registered with ELB (done by ASG) and the health check becomes InService
      eulb-describe-instance-health --show-long imagecrud
      INSTANCE		i-920744B3	InService		

    6. When they become service, you can access the service using the loadbalancer's URL
       curl imagecrud-448934789196.lb.localhost/imagecrud/
      (Note that your DNS server should be configured to be able to resolve the loadbalancer's DNS)

    7. To scale out the application, simply change the desired capacity of the autoscaling group
       euscale-set-desired-capacity -c 2 imagecrud

